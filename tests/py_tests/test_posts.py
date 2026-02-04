import tests.conftest

def test_get_all_posts(authorized_client, test_user, test_posts):
    res = authorized_client.get("/posts")
    results = res.json()
    assert res.status_code == 200
    assert results[0]['title'] == 'first title'
    