import socket,threading,subprocess,json,sys,time,pathlib,platform
backend=sys.argv[1];out=pathlib.Path('/out');events=[];rules={};port=45001

def cmd(*args):
 p=subprocess.run([backend,*args],capture_output=True,text=True,timeout=10);events.append(dict(command=p.args,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr,t_ns=time.monotonic_ns()));p.check_returncode();return p.stdout
ready=threading.Event()
def serve():
 server=socket.socket();server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);server.bind(('127.0.0.1',port));server.listen();ready.set()
 def echo(c):
  with c:
   try:
    while True:
     b=c.recv(1024)
     if not b:return
     c.sendall(b)
   except OSError:pass
 while True:
  c,_=server.accept();threading.Thread(target=echo,args=(c,),daemon=True).start()
threading.Thread(target=serve,daemon=True).start();assert ready.wait(3)
def connect():
 s=socket.socket();s.settimeout(1);s.connect(('127.0.0.1',port));return s
def probe(s=None):
 owned=s is None
 try:
  if owned:s=connect()
  token=('probe-'+str(time.monotonic_ns())).encode();s.sendall(token);data=s.recv(1024);return dict(success=data==token,error=None,t_ns=time.monotonic_ns())
 except OSError as e:return dict(success=False,error=type(e).__name__+': '+str(e),t_ns=time.monotonic_ns())
 finally:
  if owned and s is not None:s.close()
def policy(name):
 cmd('-F','ROLLBACK_STUDY')
 if name=='allow':cmd('-A','ROLLBACK_STUDY','-j','ACCEPT')
 else:
  if name=='snapshot':cmd('-A','ROLLBACK_STUDY','-m','conntrack','--ctstate','ESTABLISHED','-j','ACCEPT')
  cmd('-A','ROLLBACK_STUDY','-p','tcp','-j','REJECT','--reject-with','tcp-reset')
 return cmd('-S','ROLLBACK_STUDY')
try:
 version=cmd('--version');preflight=probe();assert preflight['success']
 cmd('-N','ROLLBACK_STUDY');cmd('-A','OUTPUT','-o','lo','-p','tcp','--dport',str(port),'-j','ROLLBACK_STUDY')
 rules['initial']=policy('snapshot');initial=probe();assert not initial['success']
 rules['allow']=policy('allow');session=connect();allowed=probe(session);assert allowed['success']
 rules['restored']=policy('snapshot');restored_session=probe(session);restored_fresh=probe()
 rules['revocation']=policy('revoke');revoked_session=probe(session);revoked_fresh=probe();session.close()
 result=dict(backend=backend,version=version,kernel=platform.release(),preflight=preflight,initial_fresh=initial,allow_session=allowed,restored_session=restored_session,restored_fresh=restored_fresh,revoked_session=revoked_session,revoked_fresh=revoked_fresh,rules_identical=rules['initial']==rules['restored'],rules=rules,scope='Known-behavior local loopback feasibility only')
 (out/'results.json').write_text(json.dumps(result,indent=2))
 assert result['rules_identical'] and not restored_fresh['success'] and not revoked_fresh['success'] and not revoked_session['success']
 print(json.dumps(result))
finally:(out/'commands.json').write_text(json.dumps(events,indent=2))
