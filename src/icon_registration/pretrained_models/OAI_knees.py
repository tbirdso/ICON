import torch.nn.functional as F
import torch
import random

from ..mermaidlite import compute_warped_image_multiNC, identity_map_multiN
from .. import inverseConsistentNet
from .. import networks
from .. import network_wrappers

import numpy as np


def OAI_knees_registration_model(pretrained=True):
    # The definition of our final 4 step registration network.

    phi = network_wrappers.FunctionFromVectorField(
        networks.tallUNet(unet=networks.UNet2ChunkyMiddle, dimension=3)
    )
    psi = network_wrappers.FunctionFromVectorField(networks.tallUNet2(dimension=3))

    pretrained_lowres_net = network_wrappers.DoubleNet(phi, psi)

    hires_net = network_wrappers.DoubleNet(
            network_wrappers.DownsampleNet(pretrained_lowres_net, dimension=3),
            network_wrappers.FunctionFromVectorField(networks.tallUNet2(dimension=3)),
        )

    fourth_net = inverseConsistentNet.InverseConsistentNet(
        network_wrappers.DoubleNet(
            hires_net, 
            network_wrappers.FunctionFromVectorField(networks.tallUNet2(dimension=3)),
        ),  
        lambda x, y: (x - y) **2,
        3600,
    )

    BATCH_SIZE = 3
    SCALE = 2  # 1 IS QUARTER RES, 2 IS HALF RES, 4 IS FULL RES
    input_shape = [BATCH_SIZE, 1, 40 * SCALE, 96 * SCALE, 96 * SCALE]

    network_wrappers.assignIdentityMap(fourth_net, input_shape)

    if pretrained:
        from os.path import exists
        if not exists("pretrained_OAI_model"):
            print("Downloading pretrained model (1.2 GB)")
            import urllib.request
            urllib.request.urlretrieve(
              "https://github.com/HastingsGreer/InverseConsistency/releases/download/pretrained_oai_model/knee_aligner_resi_net99900", "pretrained_OAI_model")

        trained_weights = torch.load("pretrained_OAI_model")
        fourth_net.load_state_dict(trained_weights)

    net = fourth_net
    BATCH_SIZE = 2
    network_wrappers.adjust_batch_size(net, BATCH_SIZE)
    net.cuda()
    net.eval()
    return net

