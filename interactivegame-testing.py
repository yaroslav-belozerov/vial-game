import unittest
import interactivegame as g


class Testing(unittest.TestCase):
    def test(self):
        window = g.InteractiveGame()
        window.setup()
        g.arcade.run()
        for block in window.blocks:
            self.assertTrue(window.check_max_same_container(block))


if __name__ == '__main__':
    unittest.main()
