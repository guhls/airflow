from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import Athena
from diagrams.custom import Custom
from diagrams.onprem.compute import Server
from diagrams.onprem.database import Postgresql as PostgreSQL
from diagrams.programming.language import Python

path_root = Path(__file__).parent

graph_attr = {
    "bgcolor": "white",
}


def diagram_1():
    with Diagram(
            "covid19_data_modeling",
            show=False,
            filename="covid19_data_modeling",
            direction="LR",
            graph_attr=graph_attr):

        dbs = Athena("view")

        with Cluster("DAG"):
            dag = [
                Python("extract_data"),
                Python("process_data"),
                Python("upload_data")]

        with Cluster("get/add data"):
            primary = [PostgreSQL("check"), Server("cnes")]

        sheets = Custom(
            "Google Sheets",
            f"{path_root}/resources/sheets-sheet-svgrepo-com.png")

        dag[0] >> dag[1] >> primary

        dag[1] >> dag[2] >> sheets

        dbs << dag[0]


def diagram_2():
    with Diagram("process_data", show=False):
        with Cluster("get or add data"):
            primary = [
                PostgreSQL("check"),
                Server("cnes")]

        primary[0] - Edge(label="collect") - primary[1]
        primary[0] >> Edge(label="CO_CEP") >> Python("modeling")


if __name__ == "__main__":
    diagram_1()
