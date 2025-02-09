aws_region        = "eu-central-1"
availability_zone = "eu-central-1a"
ami_id            = "ami-00060fac2f8c42d30"
instance_type     = "t2.micro"
root_volume_size  = 8
s3_bucket_name    = "dkedu"
key_name          = "cks"
stack_name        = "rag1"

rag_frontend_instance_role = "frontend"
rag_backend_instance_role  = "backend"
vectordb_instance_role    = "vectordb"
vectordb_cluster_name     = "vectordb-cluster"

kafka_instance_role    = "kafka"
kafka_cluster_name     = "kafka-cluster"

redis_primary_instance_role    = "redis_primary"
redis_secondary_instance_role    = "redis_secondary"
redis_cluster_name     = "redis-cluster"

prometheus_instance_role = "prometheus"
grafana_instance_role    = "grafana"
prometheus_grafana_cluster_name = "prometheus-grafana-cluster"

elasticsearch_instance_role = "elasticsearch"
fluentd_instance_role = "fluentd"
kibana_instance_role = "kibana"
efk_cluster_name = "efk-cluster"