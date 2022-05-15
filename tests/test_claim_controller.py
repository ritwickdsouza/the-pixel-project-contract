from brownie import Canvas
from brownie import CanvasController

from scripts.utils import get_account


def test_set_royalty_wallet():
    # given
    deploy_account = get_account(0)
    canvas_controller = CanvasController.deploy({"from": deploy_account})

    # when
    royalty_wallet = get_account(1)
    tx = canvas_controller.setRoyaltyWallet(royalty_wallet)
    tx.wait(1)

    # then
    assert canvas_controller.royaltyWallet() == royalty_wallet.address


def test_set_canvas_contract():
    # given
    deploy_account = get_account(0)
    canvas_controller = CanvasController.deploy({"from": deploy_account})

    # when
    canvas_contract = get_account(1)
    tx = canvas_controller.setCanvasContract(canvas_contract)
    tx.wait(1)

    # then
    assert canvas_controller.canvasContract() == canvas_contract.address


def test_get_pixel_price_init():
    # given
    deploy_account = get_account(0)
    canvas = Canvas.deploy({"from": deploy_account})
    canvas_controller = CanvasController.deploy({"from": deploy_account})
    tx = canvas_controller.setCanvasContract(canvas.address)
    tx.wait(1)
    base_price = canvas_controller.BASE_PRICE()

    # when / then
    assert canvas_controller.getPixelPrice(2, 3) == (base_price, 0)


def test_claim_pixel():
    # given
    deploy_account = get_account(0)

    canvas = Canvas.deploy({"from": deploy_account})
    canvas_controller = CanvasController.deploy({"from": deploy_account})

    royalty_wallet = get_account(1)
    tx = canvas_controller.setRoyaltyWallet(royalty_wallet)
    tx.wait(1)
    tx = canvas_controller.setCanvasContract(canvas.address)
    tx.wait(1)

    tx = canvas.setCanvasControllerContract(canvas_controller.address)
    tx.wait(1)

    x, y, color, user_account = 3, 4, 3, get_account(2)
    pixel_price, _ = canvas_controller.getPixelPrice(x, y)
    base_price = canvas_controller.BASE_PRICE()

    # when
    tx = canvas_controller.claimPixel(x, y, color, {"from": user_account, "value": pixel_price + 100})
    tx.wait(1)

    # then
    assert canvas.pixelColorMap(x, y) == color
    assert canvas.pixelOwnerMap(x, y) == user_account.address
    assert canvas.pixelClaimCountMap(x, y) == 1
    assert canvas_controller.getPixelPrice(x, y) == (2 * base_price, base_price)
