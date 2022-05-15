from brownie import Canvas
from brownie.exceptions import VirtualMachineError
import pytest

from scripts.utils import get_account


def test_set_canvas_controller_contract():
    # given
    deploy_account = get_account(0)
    canvas = Canvas.deploy({"from": deploy_account})

    # when
    canvas_controller_contract = get_account(1)
    tx = canvas.setCanvasControllerContract(canvas_controller_contract)
    tx.wait(1)

    # then
    assert canvas.canvasControllerContract() == canvas_controller_contract.address


def test_initial_pixel_color_map():
    # given
    deploy_account = get_account(0)
    canvas = Canvas.deploy({"from": deploy_account})
    m, n = canvas.M(), canvas.N()

    # when / then
    assert canvas.getPixelColorMap() == tuple(tuple(0 for _ in range(m)) for _ in range(n))


def test_initial_pixel_color_row():
    # given
    deploy_account = get_account(0)
    canvas = Canvas.deploy({"from": deploy_account})
    m, n = canvas.M(), canvas.N()

    # when / then
    assert canvas.getPixelColorRow(0) == tuple(0 for _ in range(m))


def test_claim_pixel_owner():
    # given
    deploy_account = get_account(0)
    canvas = Canvas.deploy({"from": deploy_account})
    x, y, color, claimed_by = 3, 5, 3, get_account(1)

    # when
    tx = canvas.claimPixel(x, y, color, claimed_by)
    tx.wait(1)
    tx = canvas.claimPixel(x, y, color, claimed_by)
    tx.wait(1)

    # then
    assert canvas.pixelColorMap(3, 5) == color
    assert canvas.pixelOwnerMap(3, 5) == claimed_by.address
    assert canvas.pixelClaimCountMap(3, 5) == 2


def test_claim_pixel_claim_controller_contract():
    # given
    deploy_account = get_account(0)
    canvas = Canvas.deploy({"from": deploy_account})
    canvas_controller_contract = get_account(1)
    tx = canvas.setCanvasControllerContract(canvas_controller_contract)
    tx.wait(1)

    x, y, color, claimed_by = 3, 5, 3, get_account(1)

    # when
    tx = canvas.claimPixel(x, y, color, claimed_by, {"from": canvas_controller_contract})
    tx.wait(1)
    tx = canvas.claimPixel(x, y, color, claimed_by)
    tx.wait(1)

    # then
    assert canvas.pixelColorMap(3, 5) == color
    assert canvas.pixelOwnerMap(3, 5) == claimed_by.address
    assert canvas.pixelClaimCountMap(3, 5) == 2


def test_claim_pixel_unknown_not_allowed():
    # given
    deploy_account = get_account(0)
    canvas = Canvas.deploy({"from": deploy_account})
    x, y, color, claimed_by = 3, 5, 3, get_account(1)

    # when
    unknown = get_account(1)
    with pytest.raises(VirtualMachineError) as exec_info:
        tx = canvas.claimPixel(x, y, color, claimed_by, {"from": unknown})
        tx.wait(1)

    # then
    assert exec_info.value.message == "VM Exception while processing transaction: revert Permission denied"
