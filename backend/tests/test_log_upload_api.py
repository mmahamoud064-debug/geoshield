def test_log_upload_reports_processed_and_skipped_lines(client):
    body=('8.8.8.8 - - [07/Sep/2026:10:15:00 +0000] "GET / HTTP/1.1" 200 12 "-" "demo"\n''malformed\n')
    response=client.post("/api/logs/upload",files={"file":("access.log",body,"text/plain")})
    assert response.status_code == 200
    assert response.json()["processed"] == 1
    assert response.json()["skipped"] == 1
