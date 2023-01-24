from pathlib import Path

from diagrams import Cluster, Diagram
from diagrams.aws.analytics import Athena
from diagrams.custom import Custom
from diagrams.generic.database import SQL
from diagrams.onprem.compute import Server
from diagrams.programming.language import Python

path_root = Path(__file__).parent

graph_attr = {
    "bgcolor": "transparent",
}

with Diagram(
        "covid19_data_modeling",
        show=False,
        filename="covid19_data_modeling",
        direction="LR",
        graph_attr=graph_attr):

    with Cluster("sources"):
        dbs = Athena("athena")

    with Cluster("DAG"):
        dag = [
            Python("extract_data"),
            Python("upload_data")]

        with Cluster("process_data"):
            primary = [SQL("table"), Server("API")]
            primary[1] - primary[0]

    sheets = Custom(
        "Google Sheets",
        f"{path_root}/resources/sheets-sheet-svgrepo-com.png")

    dag[0] >> primary[0] >> dag[1]
    dag[1] >> sheets

    dbs >> dag[0]
