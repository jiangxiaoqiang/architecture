from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.analytics import Spark
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.aggregator import Fluentd
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.network import Nginx
from diagrams.onprem.queue import Kafka
from diagrams.onprem.client import Users

with Diagram(name="TeXHub Architecture", show=False):
    users = Users("Users")
    openresty = Nginx("OpenResty")
    ingress = Nginx("ingress")

    with Cluster("Service Cluster"):
        grpcsvc = [
            Server("texhub-service")
            ]

    with Cluster("Cache HA"):
        primary = Redis("session")
        primary - Edge(color="brown", style="dashed") - Redis("replica") << Edge(label="collect") 
        grpcsvc >> Edge(color="brown") >> primary

    with Cluster("Database HA"):
        primary = PostgreSQL("users")
        primary - Edge(color="brown", style="dotted") - PostgreSQL("replica") << Edge(label="collect")
        grpcsvc >> Edge(color="black") >> primary
    
    with Cluster("Logging Center"):
        aggregator = Fluentd("logging")
        aggregator >> Edge(label="parse") >> Kafka("stream") >> Edge(color="black", style="bold") >> Spark("analytics")
    
    with Cluster("Monitoring Center"):
        metrics = Prometheus("metric")
        metrics << Edge(color="firebrick", style="dashed") << Grafana("monitoring")

    grpcsvc >> metrics
    ingress >> Edge(color="darkgreen") << grpcsvc >> Edge(color="darkorange") >> aggregator
    openresty >> Edge(color="darkgreen") <<ingress
    users >> Edge(color="darkgreen") << openresty 
