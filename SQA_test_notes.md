## SQA test notes

### Check 'happy path'
1. make POST requests to create two tubes, noting down their barcodes
curl -H "Content-Type: application/json" -X POST http://localhost:5000/tubes
Output: "1656279898"
Output: "1656279905"

2. make a PATCH request to update their statuses
curl -H "Content-Type: application/json" -X PATCH -d '{"body": [{"barcode": "1656279898", "status": "positive"},{"barcode": "1656279905", "status": "registered"}]}' http://localhost:5000/tubes
Output: 
"2 tubes updated, 0 barcodes not found: [],  0 invalid lines (missing barcode or status): []."


3. make a GET request to get all tubes in registered state, and confirm that the results include only the second tube
curl -H "Content-Type: application/json" -X GET http://localhost:5000/tubes
Output: 
[
    {
        "barcode": "1656279905",
        "user_id": 0,
        "id": 14,
        "status": "registered"
    }
]

### Check edge cases
4. Make a PATCH request including lines with (1) no barcode given, (2) no status given, (3) a barcode we don't have
curl -H "Content-Type: application/json" -X PATCH -d '{"body": [{"user_id":"342-AB4", "status": "positive"},{"barcode": "1656279905"}, {"barcode": "abc", "status": "registered"}]}' http://localhost:5000/tubes

Output: 
"0 tubes updated, 1 barcodes not found: ['abc'],  2 invalid lines (missing barcode or status): [{'user_id': '342-AB4', 'status': 'positive'}, {'barcode': '1656279905'}]."

