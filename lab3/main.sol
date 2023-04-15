// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Manager {
    bool public have_marker;
    mapping (address => bool) public requestedWorkers;

    modifier onlyWorker {
        require(requestedWorkers[msg.sender], "Can only be called by the worker with the marker");
        _;
    }
    
    constructor() {
        have_marker = true;
    }
    
    // Function to receive Ether. msg.data must be empty
    receive() external payable {
        if (!requestedWorkers[msg.sender]) {
            requestedWorkers[msg.sender] = false;
        }
        if (msg.value >=5 wei && have_marker) {
            requestedWorkers[msg.sender] = true;
            have_marker = false;
        } else if (msg.value < 5 wei) {
            (bool sent,) = payable(msg.sender).call{value: msg.value}("");
            assert(1==0 && sent);
        }
    }

    // Fallback function is called when msg.data is not empty
    fallback() external payable {}

    function returnMarker() external onlyWorker returns (bool) {
        if (!have_marker) {
            have_marker = true;
            requestedWorkers[msg.sender] = false;
            return true;
        }

        return false;
    }
}

contract Worker {
    Manager manager;
    string public last_op_status;
    bool public have_marker;

    constructor(address _manager) {
        manager = Manager(payable(_manager));
        last_op_status = "Init";
        have_marker = false;
    }

    // Function to receive Ether. msg.data must be empty
    receive() external payable {}

    // Fallback function is called when msg.data is not empty
    fallback() external payable {}

    function requestMarker() public payable {
        if (have_marker) {
            last_op_status = "Repeat request";
            return;
        }

        if (!manager.have_marker()) {
            last_op_status = "Already taken";
            return;
        }

        last_op_status = "Marker available";

        (bool sent,) = payable(address(manager)).call{value: msg.value}("");

        if (sent) {
            have_marker = true;
            last_op_status = "Got marker";
        } else {
            last_op_status = "Low fund";
        }
    }

    function returnMarker() public {
        require(have_marker, "Don't have marker to return");

        require(manager.returnMarker(), "Was not able to return the marker");
        
        have_marker = false;
        last_op_status = "Released";
    }
}