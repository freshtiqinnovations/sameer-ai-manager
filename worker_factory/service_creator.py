import sys,os,json
name=sys.argv[1] if len(sys.argv)>1 else ""
worker_file=sys.argv[2] if len(sys.argv)>2 else ""
if not name or not worker_file:
 print("USE: service_creator.py worker_name worker_file"); raise SystemExit(1)
svc=f"/root/sameer_ai_manager/worker_factory/generated_services/{name}.service"
content=f"""[Unit]
Description=Sameer Generated Worker {name}
After=network.target

[Service]
Type=simple
WorkingDirectory=/root/sameer_ai_manager/worker_factory/generated
ExecStart=/root/sameer_ai_manager/venv/bin/python {worker_file}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
open(svc,"w").write(content)
print("SERVICE_FILE_CREATED",svc)
