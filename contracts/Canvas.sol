// SPDX-License-Identifier: MIT
pragma solidity ^0.8.8;

import "@openzeppelin/contracts/access/Ownable.sol";

contract Canvas is Ownable {
    address public canvasControllerContract;

    uint public constant M = 10;
    uint public constant N = 10;
    uint8[M][N] public pixelColorMap;
    address[M][N] public pixelOwnerMap;
    uint256[M][N] public pixelClaimCountMap;

    function setCanvasControllerContract(address _canvasControllerContract)
        public
        onlyOwner
    {
        canvasControllerContract = _canvasControllerContract;
    }

    modifier onlyCanvasControllerOrOwner() {
        require(
            msg.sender == owner() || msg.sender == canvasControllerContract,
            "Permission denied"
        );
        _;
    }

    function claimPixel(
        uint xCoord,
        uint yCoord,
        uint8 pixelColor,
        address claimedBy
    ) public onlyCanvasControllerOrOwner {
        pixelColorMap[xCoord][yCoord] = pixelColor;
        pixelOwnerMap[xCoord][yCoord] = claimedBy;
        pixelClaimCountMap[xCoord][yCoord] =
            pixelClaimCountMap[xCoord][yCoord] +
            1;
    }

    function getPixelColorMap() public view returns (uint8[M][N] memory) {
        return pixelColorMap;
    }

    function getPixelColorRow(uint xCoord)
        public
        view
        returns (uint8[M] memory)
    {
        return pixelColorMap[xCoord];
    }
}
