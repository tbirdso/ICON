import unittest


class Test2DRegistrationTrain(unittest.TestCase):
    def test_2d_registration_train(self):

        import icon_registration.data as data
        import icon_registration.networks as networks
        import icon_registration.network_wrappers as network_wrappers
        import icon_registration.train as train
        import icon_registration.inverseConsistentNet as inverseConsistentNet

        import numpy as np
        import torch
        import random
        import os

        batch_size = 128

        d1, d2 = data.get_dataset_triangles(
            "train", data_size=50, hollow=False, batch_size=batch_size
        )
        d1_t, d2_t = data.get_dataset_triangles(
            "test", data_size=50, hollow=False, batch_size=batch_size
        )

        lmbda = 2048
        random.seed(1)
        torch.manual_seed(1)
        torch.cuda.manual_seed(1)
        np.random.seed(1)
        print("=" * 50)
        net = inverseConsistentNet.InverseConsistentNet(
            network_wrappers.FunctionFromVectorField(networks.tallUNet2(dimension=2)),
            # Our image similarity metric. The last channel of x and y is whether the value is interpolated or extrapolated,
            # which is used by some metrics but not this one
            lambda x, y: torch.mean((x[:, :1] - y[:, :1]) ** 2),
            lmbda,
        )

        input_shape = next(iter(d1))[0].size()
        network_wrappers.assignIdentityMap(net, input_shape)
        net.cuda()
        optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
        net.train()

        y = np.array(train.train2d(net, optimizer, d1, d2, epochs=50))

        # Test that image similarity is good enough
        self.assertLess(np.mean(y[-5:, 1]), 0.1)

        # Test that folds are rare enough
        self.assertLess(np.mean(np.exp(y[-5:, 3] - 0.1)), 2)
        print(y)
