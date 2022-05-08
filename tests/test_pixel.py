import pytest
from brownie import Pixel
from brownie.exceptions import VirtualMachineError

from scripts.utils import get_account


def test_inital_total_supply_zero():
    # given
    account = get_account()
    pixel = Pixel.deploy({"from": account})

    # when
    actual = pixel.totalSupply()

    # then
    assert actual == 0


def test_set_grid_size():
    # given
    account = get_account()
    pixel = Pixel.deploy({"from": account})

    # when
    grid_size = (2, 3)
    tx = pixel.setGridSize(*grid_size)
    tx.wait(1)

    # then
    assert (pixel.gridSizeX(), pixel.gridSizeY()) == grid_size


@pytest.mark.parametrize(
    "x_coord,y_coord,expected",
    [(0, 0, True), (2, 3, True), (4, 4, True), (4, 5, False), (5, 4, False)],
)
def test_is_valid_coords(x_coord, y_coord, expected):
    # given
    account = get_account()
    pixel = Pixel.deploy({"from": account})
    tx = pixel.setGridSize(5, 5)
    tx.wait(1)

    # when
    is_valid_coords = pixel.isValidCoords(x_coord, y_coord)

    # when
    assert is_valid_coords == expected


def test_display_coords():
    # given
    account = get_account()
    pixel = Pixel.deploy({"from": account})

    # when
    actual = pixel.hashCoordinates(1, 2)

    # then
    assert actual


def test_set_canvas_contract():
    # given
    account = get_account()
    pixel = Pixel.deploy({"from": account})

    # when
    canvas_contract_address = get_account(1)
    tx = pixel.setCanvasContract(canvas_contract_address)
    tx.wait(1)

    # then
    assert pixel.canvasContract() == canvas_contract_address


@pytest.mark.parametrize(
    "x_coord,y_coord,expected",
    [(1, 1, True), (0, 0, False)],
)
def test_is_pixel_minted(x_coord, y_coord, expected):
    # given
    deploy_account = get_account(0)
    pixel = Pixel.deploy({"from": deploy_account})
    pixel.setGridSize(2, 3)
    user_account = get_account(1)
    pixel.mintPixel(1, 1, {"from": user_account})

    # when
    tx = pixel.isPixelMinted(x_coord, y_coord)
    tx.wait(1)

    # then
    assert tx.return_value == expected
    assert pixel.ownerOf(pixel.getTokenId(1, 1).return_value) == user_account.address


def test_mint_pixel():
    # given
    account = get_account()
    pixel = Pixel.deploy({"from": account})
    pixel.setGridSize(3, 4)

    # when
    for coords in [(0, 0), (1, 1), (2, 2)]:
        tx = pixel.mintPixel(*coords)
    tx.wait(1)

    # then
    assert pixel.totalSupply() == 3


def test_get_token_id():
    # given
    account = get_account()
    pixel = Pixel.deploy({"from": account})
    pixel.setGridSize(3, 4)

    # when
    for coords in [(0, 0), (1, 1), (2, 2)]:
        tx = pixel.mintPixel(*coords)
    tx.wait(1)

    # then
    assert pixel.getTokenId(0, 0).return_value == 1
    assert pixel.getTokenId(1, 1).return_value == 2
    assert pixel.getTokenId(2, 2).return_value == 3


def test_check_canvas_address_approval_set():
    # given
    deploy_account = get_account(0)
    pixel = Pixel.deploy({"from": deploy_account})
    canvas_account = get_account(1)
    tx = pixel.setCanvasContract(canvas_account.address)
    tx = pixel.setGridSize(3, 3)

    # when
    user_account = get_account(2)
    tx = pixel.mintPixel(1, 1, {"from": user_account})
    tx.wait(1)

    # then
    expected = pixel.isApprovedForAll(user_account.address, canvas_account.address)
    assert expected == True


def test_check_token_uri_on_minted_pixel():
    # given
    account = get_account()
    pixel = Pixel.deploy({"from": account})
    pixel.setGridSize(3, 4)

    # when
    tx = pixel.mintPixel(2, 2)
    tx.wait(1)

    # then
    assert pixel.tokenURI(pixel.getTokenId(2, 2).return_value) == "TEST"


def test_pixel_already_minted_reverts_transaction():
    # given
    account = get_account()
    pixel = Pixel.deploy({"from": account})
    pixel.setGridSize(3, 4)
    pixel.mintPixel(2, 2)

    # when / then
    with pytest.raises(VirtualMachineError) as exec_info:
        tx = pixel.mintPixel(2, 2)
        tx.wait(1)

    assert (
        exec_info.value.message
        == "VM Exception while processing transaction: revert Pixel with coords already minted"
    )


def test_coordinates_provided_out_of_range():
    # given
    account = get_account()
    pixel = Pixel.deploy({"from": account})
    pixel.setGridSize(1, 1)

    # when / then
    with pytest.raises(VirtualMachineError) as exec_info:
        tx = pixel.mintPixel(2, 2)
        tx.wait(1)

    assert (
        exec_info.value.message
        == "VM Exception while processing transaction: revert Coordinates provided are out of range"
    )
