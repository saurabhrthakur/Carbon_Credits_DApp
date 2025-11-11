// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";


contract CarbonCredit is Ownable {
    struct Credit {
        uint16 id;         
        address owner;      
        uint32 amount;      
        bool retired;       
        string location;    
    }

    mapping(uint16 => Credit) public credits;
    uint16 public nextId;   // Next available credit ID

    // --- Events ---
    event CreditIssued(uint16 indexed id, address indexed owner, uint32 amount, string location);
    event CreditTransferred(uint16 indexed id, address indexed from, address indexed to, uint32 amount);
    event CreditRetired(uint16 indexed id, address indexed owner);
    event CreditLocationUpdated(uint16 indexed id, string oldLocation, string newLocation);

    // --- Constructor ---
    constructor(address initialOwner) Ownable(initialOwner) {}

    // --- Issue new credit ---
    function issueCredit(address to, uint32 amount, string calldata location) external onlyOwner {
        require(to != address(0), "Invalid address");
        require(amount > 0, "Amount must be > 0");
        require(bytes(location).length > 0, "Location required");
        require(nextId < type(uint16).max, "Max credits reached");

        nextId++;
        credits[nextId] = Credit({
            id: nextId,
            owner: to,
            amount: amount,
            retired: false,
            location: location
        });

        //  ensures internal logic consistency 
        assert(credits[nextId].id == nextId);

        emit CreditIssued(nextId, to, amount, location);
    }

    // --- Transfer credit ownership ---
    function transferCredit(uint16 id, address to, uint32 amount) external {
        Credit storage credit = credits[id];
        require(credit.owner == msg.sender, "Not owner");
        require(!credit.retired, "Already retired");
        require(amount > 0 && amount <= credit.amount, "Invalid amount");
        require(to != address(0), "Invalid recipient");

        if (amount < credit.amount) {
            // Split the credit into two entries
            credit.amount -= amount;
            nextId++;
            require(nextId < type(uint16).max, "Max credits reached");

            credits[nextId] = Credit({
                id: nextId,
                owner: to,
                amount: amount,
                retired: false,
                location: credit.location
            });

            emit CreditIssued(nextId, to, amount, credit.location);
        } else {
            // Transfer full credit
            credit.owner = to;
        }

        emit CreditTransferred(id, msg.sender, to, amount);
    }

    // --- Retire a credit ---
    function retireCredit(uint16 id) external {
        Credit storage credit = credits[id];
        require(credit.owner == msg.sender, "Not owner");
        require(!credit.retired, "Already retired");

        credit.retired = true;

        assert(credit.retired == true);
        
        emit CreditRetired(id, msg.sender);
    }

    // --- Update the location of a credit ---
    function updateCreditLocation(uint16 id, string calldata newLocation) external onlyOwner {
        Credit storage credit = credits[id];
        require(!credit.retired, "Credit retired");
        require(bytes(newLocation).length > 0, "Invalid location");

        string memory oldLocation = credit.location;
        credit.location = newLocation;

        emit CreditLocationUpdated(id, oldLocation, newLocation);
    }

    // --- View location ---
    function getCreditLocation(uint16 id) external view returns (string memory) {
        return credits[id].location;
    }
}
