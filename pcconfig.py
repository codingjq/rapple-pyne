import pynecone as pc

config = pc.Config(
    app_name="rapple",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.PROD,
    api_url="https://rapple-ws.jervas.com",
    bun_path="/home/jqwez/.bun/bin/bun",
)
