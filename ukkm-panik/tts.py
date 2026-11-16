import sys, certifi
certifi.where=lambda: "/root/.ccr/ca-bundle.crt"
import asyncio, edge_tts, json
async def main(voice,text,out,subs,rate):
    c=edge_tts.Communicate(text,voice,rate=rate,boundary="WordBoundary")
    words=[]
    with open(out,"wb") as f:
        async for ch in c.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary": words.append([ch["offset"]/1e7,(ch["offset"]+ch["duration"])/1e7,ch["text"]])
    json.dump(words,open(subs,"w"),ensure_ascii=False)
asyncio.run(main(sys.argv[1],open(sys.argv[2]).read(),sys.argv[3],sys.argv[4],sys.argv[5] if len(sys.argv)>5 else "+0%"))
