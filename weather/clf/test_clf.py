import unittest

from classify import SeaStateCLF


# 测试数据
test_value_dict = {
    0: {'wind_speed': 13.9, 'wave_height': 1.25, 'level': 6},
    1: {'wind_speed': 1.6, 'wave_height': 6, 'level': 7},
}


class TestDict(unittest.TestCase):
    def test_static(self):
        """分类测试
        """
        for _, key in enumerate(test_value_dict.keys()):
            est = SeaStateCLF(
                wind_speed=test_value_dict[key]['wind_speed'],
                wave_height=test_value_dict[key]['wave_height']
            )
            level = est.clf()
            self.assertEqual(level, test_value_dict[key]['level'])


if __name__ == '__main__':
    unittest.main()
