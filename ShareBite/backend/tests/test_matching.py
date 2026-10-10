from app.services.matching_service import distance_km, location_score, quantity_score, need_score


def test_distance_same_point_is_zero():
    assert distance_km(26.1445, 91.7362, 26.1445, 91.7362) == 0


def test_distance_score_uses_max_radius():
    assert location_score(10, 20) == 50
    assert location_score(20, 20) == 0


def test_quantity_score_compares_real_need():
    assert quantity_score(20, 10) == 50
    assert quantity_score(10, 10) == 100
    assert quantity_score(20, None) == 70


def test_need_priority_score():
    assert need_score("urgent") == 100
    assert need_score("low") < need_score("urgent")
