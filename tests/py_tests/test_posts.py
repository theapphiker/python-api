import tests.conftest

def test_get_all_posts(authorized_client, test_user, test_posts):
    res = authorized_client.get("/posts")
    results = res.json()
    assert res.status_code == 200
    titles = ['first title', '2nd title', '3rd title']
    for i in range(len(results)):
        assert results[i]['title'] in titles

def test_unauthorized_user_get_all_posts(unauthorized_client):
    res = unauthorized_client.get("/posts")
    assert res.status_code == 401

def test_unauthorized_user_get_one_posts(unauthorized_client, test_max_post_id):
    id = test_max_post_id[0]
    res = unauthorized_client.get(f"/posts/{id}")
    assert res.status_code == 401