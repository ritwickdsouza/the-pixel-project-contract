// SPDX-License-Identifier: MIT
pragma solidity ^0.8.8;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/PullPayment.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "./Canvas.sol";

contract CanvasController is Ownable, PullPayment, Pausable, ReentrancyGuard {
    using SafeMath for uint256;

    uint constant public BASE_PRICE = 200000000000000;
    address public canvasContract;
    address public royaltyWallet;

    event PixelClaimed(
        uint indexed xCoord,
        uint indexed yCoord,
        uint8 pixelColor
    );

    function setRoyaltyWallet(address _royaltyWallet) public onlyOwner {
        royaltyWallet = _royaltyWallet;
    }

    function setCanvasContract(address _canvasContract) public onlyOwner {
        canvasContract = _canvasContract;
    }

    function getPixelPrice(uint xCoord, uint yCoord)
        public
        view
        returns (uint totalPrice, uint lastOwnerPrice)
    {
        Canvas canvas = Canvas(canvasContract);
        lastOwnerPrice = SafeMath.mul(
            canvas.pixelClaimCountMap(xCoord, yCoord),
            BASE_PRICE
        );
        totalPrice = SafeMath.add(lastOwnerPrice, BASE_PRICE);
        return (totalPrice, lastOwnerPrice);
    }

    modifier isClaimable(
        uint xCoord,
        uint yCoord,
        uint8 pixelColor
    ) {
        require(xCoord < 50 && yCoord < 50);
        require(pixelColor > 0 && pixelColor < 255);
        _;
    }

    function _paintPixel(
        uint xCoord,
        uint yCoord,
        uint8 pixelColor
    ) internal returns (address lastOwner) {
        Canvas canvas = Canvas(canvasContract);
        lastOwner = canvas.pixelOwnerMap(xCoord, yCoord);
        canvas.claimPixel(xCoord, yCoord, pixelColor, msg.sender);
        return lastOwner;
    }

    function _sendBuyPayment(address lastOwner, uint lastOwnerPrice) internal {
        if (lastOwner != address(0) || lastOwnerPrice == 0) {
            _asyncTransfer(lastOwner, lastOwnerPrice);
            _asyncTransfer(royaltyWallet, BASE_PRICE);
        }
    }

    function claimPixel(
        uint xCoord,
        uint yCoord,
        uint8 pixelColor
    )
        public
        payable
        isClaimable(xCoord, yCoord, pixelColor)
        nonReentrant
        whenNotPaused
    {
        (uint totalPrice, uint lastOwnerPrice) = this.getPixelPrice(
            xCoord,
            yCoord
        );
        require(msg.value >= totalPrice);

        address lastOwner = _paintPixel(xCoord, yCoord, pixelColor);
        _sendBuyPayment(lastOwner, lastOwnerPrice);
        emit PixelClaimed(xCoord, yCoord, pixelColor);
    }
}
