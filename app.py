import os, re, uuid
from pathlib import Path
from flask import Flask, jsonify, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
load_dotenv()
BASE=Path(__file__).resolve().parent
UPLOADS=BASE/'uploads'; UPLOADS.mkdir(exist_ok=True)
app=Flask(__name__); app.config['MAX_CONTENT_LENGTH']=150*1024*1024
VIDEO={'mp4','webm','mov','m4v'}; IMAGE={'png','jpg','jpeg','webp'}; AUDIO={'mp3','wav','ogg','m4a'}
def fal():
    try:
        import fal_client
        return fal_client
    except ImportError: return None
def urls(obj):
    out=[]
    if isinstance(obj,dict):
        for k,v in obj.items():
            if isinstance(v,str) and v.startswith('http') and any(x in k.lower() for x in ('url','video','image','file')): out.append(v)
            else: out += urls(v)
    elif isinstance(obj,list):
        for v in obj: out += urls(v)
    return list(dict.fromkeys(out))
@app.get('/')
def home(): return render_template('index.html')
@app.get('/api/health')
def health():
    live=bool(os.getenv('FAL_KEY') and os.getenv('FAL_VIDEO_MODEL') and os.getenv('FAL_IMAGE_MODEL') and fal())
    return jsonify(status='ok',mode='live' if live else 'demo')
@app.post('/api/generate')
def generate():
    d=request.get_json(silent=True) or {}; kind=d.get('kind'); prompt=re.sub(r'[\x00-\x1f]','',str(d.get('prompt',''))).strip()[:3000]
    if kind not in ('video','image'): return jsonify(error='Unsupported generation type.'),400
    if len(prompt)<3: return jsonify(error='Enter a prompt with at least 3 characters.'),400
    model=os.getenv('FAL_VIDEO_MODEL' if kind=='video' else 'FAL_IMAGE_MODEL','').strip(); key=os.getenv('FAL_KEY','').strip(); client=fal()
    if not (model and key and client): return jsonify(mode='demo',message='Demo only: configure FAL_KEY and the exact model IDs in your private .env file to generate real media.'),200
    os.environ['FAL_KEY']=key
    args={'prompt':prompt}
    if kind=='video': args.update(duration=int(d.get('duration',5)),aspect_ratio=d.get('aspect','16:9'))
    else: args.update(image_size='landscape_16_9',num_images=1)
    try:
        h=client.submit(model,arguments=args)
        return jsonify(mode='live',request_id=h.request_id,model=model),202
    except Exception as e:
        app.logger.exception('Generation submit failed')
        return jsonify(error='Provider rejected the request. Check model ID, input schema, API key and credits.',detail=str(e)[:250]),502
@app.get('/api/jobs/<rid>')
def job(rid):
    if not re.fullmatch(r'[A-Za-z0-9_-]{6,120}',rid): return jsonify(error='Invalid job ID.'),400
    model=request.args.get('model','').strip()
    if not model or model not in (os.getenv('FAL_VIDEO_MODEL',''),os.getenv('FAL_IMAGE_MODEL','')): return jsonify(error='Unknown model.'),400
    client=fal()
    if not client: return jsonify(error='Provider client unavailable.'),503
    try:
        s=client.status(model,rid,with_logs=False); state=str(s).lower()
        if 'completed' in state:
            result=client.result(model,rid); return jsonify(status='completed',urls=urls(result))
        if 'failed' in state: return jsonify(status='failed',error='Provider reported generation failure.')
        return jsonify(status='processing')
    except Exception as e:
        app.logger.exception('Job poll failed'); return jsonify(error='Could not check generation status.',detail=str(e)[:200]),502
@app.post('/api/upload')
def upload():
    f=request.files.get('file')
    if not f or not f.filename: return jsonify(error='Choose a file.'),400
    filename=secure_filename(f.filename); ext=filename.rsplit('.',1)[-1].lower() if '.' in filename else ''
    if ext not in VIDEO|IMAGE|AUDIO: return jsonify(error='Unsupported media format.'),400
    name=uuid.uuid4().hex+'.'+ext; f.save(UPLOADS/name); return jsonify(url='/uploads/'+name,name=filename)
@app.get('/uploads/<path:name>')
def uploaded(name): return send_from_directory(UPLOADS,name)
@app.errorhandler(413)
def large(_): return jsonify(error='Upload exceeds 150 MB.'),413
if __name__=='__main__': app.run(host='127.0.0.1',port=int(os.getenv('PORT','5000')),debug=False)
