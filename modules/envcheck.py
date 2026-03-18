import subprocess


def check_env(env):

    result = subprocess.run(
        f"conda env list | grep {env}",
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Conda environment '{env}' not found")

    print(f"? Environment '{env}' detected")


def check_tool(env, tool):

    result = subprocess.run(
        f"conda run -n {env} which {tool}",
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"{tool} not found in environment '{env}'")

    print(f"? Tool '{tool}' found in '{env}'")