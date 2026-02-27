import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import toml

from dtw_lab.lab1 import (
    read_csv_from_google_drive,
    visualize_data,
    calculate_statistic,
    clean_data,
)

app = FastAPI()

def run_server(port: int = 80, reload: bool = False, host: str = "127.0.0.1"):
    uvicorn.run("dtw_lab.lab2:app", port=port, reload=reload, host=host)

def run_server_dev():
    run_server(port=8000, reload=True)

def run_server_prod():
    run_server(reload=False, host="0.0.0.0")

@app.get("/")
def main_route():
    return {"message": "Hello world"}


# ---------- NUEVAS RUTAS ----------

@app.get("/statistic/{measure}/{column}")
def get_statistic(measure: str, column: str):
    """
    measure: por ejemplo "mean", "median", "min", "max", "std"...
    column: nombre de columna del CSV
    """
    df = read_csv_from_google_drive("1eKiAZKbWTnrcGs3bqdhINo1E4rBBpglo")
    df = clean_data(df)

    try:
        value = calculate_statistic(measure,df[column])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"measure": measure, "column": column, "value": value}


@app.get("/visualize/{graph_type}")
def get_visualization(graph_type: str):
    """
    visualize_data(...) debe generar 3 imágenes en la carpeta graphs/.
    graph_type selecciona cuál devolver.
    """
    df = read_csv_from_google_drive("1eKiAZKbWTnrcGs3bqdhINo1E4rBBpglo")
    df = clean_data(df)

    visualize_data(df)

    graphs_dir = Path("graphs")
    if not graphs_dir.exists():
        raise HTTPException(status_code=500, detail="graphs/ folder was not created.")

    mapping = {
        "hist": graphs_dir / "histograms.png",
        "box": graphs_dir / "boxplots.png",
        "scatter": graphs_dir / "scatter_plots.png",
    }

    if graph_type not in mapping:
        raise HTTPException(status_code=400, detail=f"graph_type must be one of {list(mapping.keys())}")

    file_path = mapping[graph_type]
    if not file_path.exists():
        raise HTTPException(status_code=500, detail=f"Expected file not found: {file_path}")

    return FileResponse(path=str(file_path), media_type="image/png")


@app.get("/version")
def get_visualization_version():
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise HTTPException(status_code=500, detail="pyproject.toml not found at repo root")

    data = toml.loads(pyproject_path.read_text(encoding="utf-8"))

    try:
        version = data["project"]["version"]
    except Exception:
        raise HTTPException(status_code=500, detail="Could not read [project].version from pyproject.toml")

    return {"version": version}