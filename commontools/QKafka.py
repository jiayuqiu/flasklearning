# coding:utf-8

from kafka import KafkaProducer


def on_send_success(record_metadata, logger):
    logger.info("topic: %s, partition: %s, offset: %s" % (record_metadata.topic, record_metadata.partition, record_metadata.offset))
    return "success"


def on_send_error(excp, logger):
    logger.logger.error("ERROR: %s" % excp)
    return "error"


class QKafka:
    """通过kafka进行广播测试数据"""
    def __init__(self, ship_id, kafka_info):
        self.ship_id = ship_id
        self.kafka_info = kafka_info

    def create_producers(self):
        """生成kafka生产者"""
        kafka_dict = {}
        for key in self.kafka_info:
            kafka_producer_dict = self.kafka_info[key]
            _producer = KafkaProducer(
                bootstrap_servers=['{host}:{port}'.format(
                    host=kafka_producer_dict["host"],
                    port=kafka_producer_dict["port"]
                )]
            )
            kafka_dict[key] = _producer
        return kafka_dict
