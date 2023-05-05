import src.utils.methods as umethods


class configtest:
    def __init__(self, config):
        self.iaq_sid = config.get('IAQ', 'sid')
        self.iaq_a = ('a')


if __name__ == '__main__':
    config = umethods.load_config('../../../conf/port_config.properties').get('IAQ', 'sid')
    print(config)
    # test = configtest(config)

    # print(test.iaq_sid)
    # print(test.iaq_a)
