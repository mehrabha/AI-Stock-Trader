import os

def load_env():
    env_file = os.path.join(os.getcwd(), "configs.env")

    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    formatted = line.split("#", 1)[0]
                    k, v = formatted.split('=', 1)
                    os.environ[k.strip()] = v.strip()
    else:
        raise Exception(f"No .env file found at={env_file}")

