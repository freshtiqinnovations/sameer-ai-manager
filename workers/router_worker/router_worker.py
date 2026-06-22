import sys,json

BOT_ROUTES={
 "autopilot":"/root/sameer_ai_manager/ai_worker/queue",
 "travel":"/root/sameer_ai_manager/ai_worker/queue",
 "freshtiq":"/root/sameer_ai_manager/ai_worker/queue",
 "salama":"/root/sameer_ai_manager/ai_worker/queue",
 "sameer":"/root/sameer_ai_manager/ai_worker/queue"
}

def route(bot):
    return BOT_ROUTES.get(bot,"MANAGER_REVIEW")

if len(sys.argv)>1:
    print(route(sys.argv[1]))
