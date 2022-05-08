// SPDX-License-Identifier: MIT
pragma solidity 0.8.8;

import "./Pixel.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";

contract Canvas is IERC721Receiver, Ownable, ReentrancyGuard {
    address public pixelContract;

    event PixelTransferred(
        uint256 indexed tokenId,
        uint256 xCoord,
        uint256 yCoord,
        address indexed from,
        address indexed to
    );

    function setPixelContract(address _pixelContract) public onlyOwner {
        pixelContract = _pixelContract;
    }

    function claimPixel(uint256 xCoord, uint256 yCoord)
        public
        payable
        nonReentrant
    {
        // Fetch pixel contract
        Pixel pixel = Pixel(pixelContract);

        // Check if pixel is already minted or not
        uint256 tokenId;
        if (pixel.isPixelMinted(xCoord, yCoord)) {
            // Pixel already exists, so we transfer the pixel
            tokenId = pixel.getTokenId(xCoord, yCoord);
            address originalOwner = pixel.ownerOf(tokenId);
            pixel.safeTransferFrom(originalOwner, msg.sender, tokenId);
            emit PixelTransferred(
                tokenId,
                xCoord,
                yCoord,
                originalOwner,
                msg.sender
            );
        } else {
            // Pixel does not exist, so we mint a new pixel
            pixel.mintPixel(xCoord, yCoord, msg.sender);
            tokenId = pixel.getTokenId(xCoord, yCoord);
            emit PixelTransferred(
                tokenId,
                xCoord,
                yCoord,
                address(0),
                msg.sender
            );
        }
    }

    function onERC721Received(
        address operator,
        address from,
        uint256 tokenId,
        bytes memory data
    ) public virtual override returns (bytes4) {
        return this.onERC721Received.selector;
    }
}
