from brownie import Canvas, Pixel

from scripts.utils import get_account


def test_set_pixel_contract():
    # given
    deploy_account = get_account(0)
    canvas = Canvas.deploy({"from": deploy_account})

    # when
    pixel_account = get_account(1)
    tx = canvas.setPixelContract(pixel_account.address)
    tx.wait(1)

    # then
    assert canvas.pixelContract() == pixel_account.address


def test_claim_pixel_fresh_mint():
    # given
    deploy_account = get_account(0)

    canvas = Canvas.deploy({"from": deploy_account})
    pixel = Pixel.deploy({"from": deploy_account})

    pixel.setCanvasContract(canvas.address)
    canvas.setPixelContract(pixel.address)

    tx = pixel.setGridSize(3, 3)
    tx.wait(1)

    # when
    user_account = get_account(1)
    tx = canvas.claimPixel(1, 1, {"from": user_account})
    tx.wait()

    # then
    assert pixel.totalSupply() == 1
    assert pixel.ownerOf(pixel.getTokenId(1, 1).return_value) == user_account.address


def test_claim_pixel_already_minted():
    # given
    deploy_account = get_account(0)

    canvas = Canvas.deploy({"from": deploy_account})
    pixel = Pixel.deploy({"from": deploy_account})

    pixel.setCanvasContract(canvas.address)
    canvas.setPixelContract(pixel.address)

    pixel.setGridSize(3, 3)
    user_account_1 = get_account(1)
    tx = pixel.mintPixel(1, 1, {"from": user_account_1})
    tx.wait(1)

    # when
    user_account_2 = get_account(2)
    canvas.claimPixel(1, 1, {"from": user_account_2})

    # then
    assert pixel.totalSupply() == 1
    assert pixel.ownerOf(pixel.getTokenId(1, 1).return_value) == user_account_2.address
