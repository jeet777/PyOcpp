import pytest
from ocpp.v20 import ChargePoint as cp
from ocpp.routing import on, create_route_map
from ocpp.v16.enums import Action


def test_getters_should_not_be_called_during_routemap_setup():
    class ChargePoint(cp):
        @property
        def foo(self):
            raise RuntimeError("this will be raised")

    try:
        ChargePoint("blah", None)
    except RuntimeError as e:
        assert str(e) == "this will be raised"
        pytest.fail("Getter was called during ChargePoint creation")


def test_multiple_classes_with_same_name_for_handler():
    class ChargerA(cp):
        @on(Action.Heartbeat)
        def heartbeat(self, **kwargs):
            pass

    class ChargerB(cp):
        @on(Action.Heartbeat)
        def heartbeat(self, **kwargs):
            pass

    A = ChargerA("A", None)
    B = ChargerB("B", None)
    route_mapA = create_route_map(A)
    route_mapB = create_route_map(B)
    assert route_mapA["Heartbeat"] != route_mapB["Heatbeat"]
