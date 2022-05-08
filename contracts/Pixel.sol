// SPDX-License-Identifier: MIT
pragma solidity 0.8.8;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract Pixel is ERC721URIStorage, Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenId;

    address public canvasContract;

    uint256 public gridSizeX;
    uint256 public gridSizeY;

    mapping(bytes32 => uint256) public mintedPixels;

    constructor() ERC721("Pixel", "PIXEL") {}

    function totalSupply() public view returns (uint256) {
        return _tokenId.current();
    }

    function hashCoordinates(uint256 xCoord, uint256 yCoord)
        public
        view
        returns (bytes32)
    {
        bytes32 hashedCoordinates = keccak256(abi.encodePacked(xCoord, yCoord));
        return hashedCoordinates;
    }

    function setCanvasContract(address _canvasContract) public onlyOwner {
        canvasContract = _canvasContract;
    }

    function setGridSize(uint256 _gridSizeX, uint256 _gridSizeY)
        public
        onlyOwner
    {
        gridSizeX = _gridSizeX;
        gridSizeY = _gridSizeY;
    }

    function isValidCoords(uint256 xCoord, uint256 yCoord)
        public
        view
        returns (bool)
    {
        bool result = xCoord < gridSizeX && yCoord < gridSizeY;
        return result;
    }

    function getTokenId(uint256 xCoord, uint256 yCoord)
        public
        returns (uint256)
    {
        require(
            isValidCoords(xCoord, yCoord),
            "Coordinates provided are out of range"
        );
        bytes32 hashedCoordinates = hashCoordinates(xCoord, yCoord);
        return mintedPixels[hashedCoordinates];
    }

    function isPixelMinted(uint256 xCoord, uint256 yCoord)
        public
        returns (bool)
    {
        return getTokenId(xCoord, yCoord) > 0;
    }

    function _mintPixel(
        uint256 xCoord,
        uint256 yCoord,
        address _receiver
    ) internal returns (uint256) {
        require(
            !isPixelMinted(xCoord, yCoord),
            "Pixel with coords already minted"
        );

        // Fetch tokenId
        _tokenId.increment();
        uint256 tokenId = _tokenId.current();

        // Mint `Pixel` token
        _safeMint(_receiver, tokenId);
        string memory tokenURI = string("TEST"); // TODO: Set pixel metadata
        _setTokenURI(tokenId, tokenURI);
        bytes32 hashedCoordinates = hashCoordinates(xCoord, yCoord);
        mintedPixels[hashedCoordinates] = tokenId;

        // Give `Canvas` access to transfering `Pixel` token
        setApprovalForAll(canvasContract, true);
    }

    function mintPixel(
        uint256 xCoord,
        uint256 yCoord,
        address _receiver
    ) public nonReentrant returns (uint256) {
        _mintPixel(xCoord, yCoord, _receiver);
    }

    function mintPixel(uint256 xCoord, uint256 yCoord)
        public
        nonReentrant
        returns (uint256)
    {
        _mintPixel(xCoord, yCoord, msg.sender);
    }
}
