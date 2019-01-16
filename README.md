# tictactoe-rest-backend
API Available at `https://tictactoe-rest-backend.herokuapp.com/`

### Endpoints:
* __GET__ /session: *create a new session*
    * Request data: none
    * Response data: code 200: session id; code 500 - error message
* __POST__ /session/<session_id>: *register a move*
    * Request data: {"player": either "X" or "O", "updated_field": int}
    * Response data: {"xs": int, "os": int, "winner": "X" or "O" or "-"}
    
 #### Test endpoints (dummyversion branch only):
 * __GET__ /test: *get a test message*
    * Request data: none
    * Response data: Message
 * __POST__ /test/<data_>: *echo*
    * Request data: urlencoded string in request url
    * Response data: same message 
