#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import UserFieldEntries
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_field,
    login_as_user,
    register_user,
)


def test_new_fields_show_on_pages():
    app = create_ctfd()
    with app.app_context():
        register_user(app)

        gen_field(app.db)

        with login_as_user(app) as client:
            r = client.get("/register")
            assert "CustomField" in r.get_data(as_text=True)
            assert "CustomFieldDescription" in r.get_data(as_text=True)

            r = client.get("/settings")
            assert "CustomField" in r.get_data(as_text=True)
            assert "CustomFieldDescription" in r.get_data(as_text=True)

            r = client.patch(
                "/api/v1/users/me",
                json={"fields": [{"field_id": 1, "value": "CustomFieldEntry"}]},
            )
            resp = r.get_json()
            assert resp["success"] is True
            assert resp["data"]["fields"][0]["value"] == "CustomFieldEntry"
            assert resp["data"]["fields"][0]["description"] == "CustomFieldDescription"
            assert resp["data"]["fields"][0]["name"] == "CustomField"
            assert resp["data"]["fields"][0]["field_id"] == 1

            r = client.get("/user")
            resp = r.get_data(as_text=True)
            assert "CustomField" in resp
            assert "CustomFieldEntry" in resp

            r = client.get("/users/2")
            resp = r.get_data(as_text=True)
            assert "CustomField" in resp
            assert "CustomFieldEntry" in resp
    destroy_ctfd(app)


def test_fields_required_on_register():
    app = create_ctfd()
    with app.app_context():
        gen_field(app.db)

        with app.app_context():
            with app.test_client() as client:
                client.get("/register")
                with client.session_transaction() as sess:
                    data = {
                        "name": "user",
                        "email": "user@ctfd.io",
                        "password": "password",
                        "nonce": sess.get("nonce"),
                    }
                client.post("/register", data=data)
                with client.session_transaction() as sess:
                    assert sess.get("id") is None

                with client.session_transaction() as sess:
                    data = {
                        "name": "user",
                        "email": "user@ctfd.io",
                        "password": "password",
                        "fields[1]": "custom_field_value",
                        "nonce": sess.get("nonce"),
                    }
                client.post("/register", data=data)
                with client.session_transaction() as sess:
                    assert sess["id"]
    destroy_ctfd(app)


def test_fields_properties():
    app = create_ctfd()
    with app.app_context():
        register_user(app)

        gen_field(
            app.db, name="CustomField1", required=True, public=True, editable=True
        )
        gen_field(
            app.db, name="CustomField2", required=False, public=True, editable=True
        )
        gen_field(
            app.db, name="CustomField3", required=False, public=False, editable=True
        )
        gen_field(
            app.db, name="CustomField4", required=False, public=False, editable=False
        )

        with login_as_user(app) as client:
            r = client.get("/register")
            resp = r.get_data(as_text=True)
            assert "CustomField1" in resp
            assert "CustomField2" in resp
            assert "CustomField3" in resp
            assert "CustomField4" in resp

            r = client.get("/settings")
            resp = r.get_data(as_text=True)
            assert "CustomField1" in resp
            assert "CustomField2" in resp
            assert "CustomField3" in resp
            assert "CustomField4" not in resp

            r = client.patch(
                "/api/v1/users/me",
                json={
                    "fields": [
                        {"field_id": 1, "value": "CustomFieldEntry1"},
                        {"field_id": 2, "value": "CustomFieldEntry2"},
                        {"field_id": 3, "value": "CustomFieldEntry3"},
                        {"field_id": 4, "value": "CustomFieldEntry4"},
                    ]
                },
            )
            resp = r.get_json()
            assert resp == {
                "success": False,
                "errors": {"fields": ["Field CustomField4 cannot be editted"]},
            }

            r = client.patch(
                "/api/v1/users/me",
                json={
                    "fields": [
                        {"field_id": 1, "value": "CustomFieldEntry1"},
                        {"field_id": 2, "value": "CustomFieldEntry2"},
                        {"field_id": 3, "value": "CustomFieldEntry3"},
                    ]
                },
            )
            assert r.status_code == 200

            r = client.get("/user")
            resp = r.get_data(as_text=True)
            assert "CustomField1" in resp
            assert "CustomField2" in resp
            assert "CustomField3" not in resp
            assert "CustomField4" not in resp

            r = client.get("/users/2")
            resp = r.get_data(as_text=True)
            assert "CustomField1" in resp
            assert "CustomField2" in resp
            assert "CustomField3" not in resp
            assert "CustomField4" not in resp
    destroy_ctfd(app)


def test_boolean_checkbox_field():
    app = create_ctfd()
    with app.app_context():
        gen_field(app.db, name="CustomField1", field_type="boolean", required=False)

        with app.app_context():
            with app.test_client() as client:
                r = client.get("/register")
                resp = r.get_data(as_text=True)

                # We should have rendered a checkbox input
                assert "checkbox" in resp

                with client.session_transaction() as sess:
                    data = {
                        "name": "user",
                        "email": "user@ctfd.io",
                        "password": "password",
                        "nonce": sess.get("nonce"),
                        "fields[1]": "y",
                    }
                client.post("/register", data=data)
                with client.session_transaction() as sess:
                    assert sess["id"]

        assert UserFieldEntries.query.count() == 1
        assert UserFieldEntries.query.filter_by(id=1).first().value is True

        with login_as_user(app) as client:
            r = client.get("/settings")
            resp = r.get_data(as_text=True)
            assert "CustomField1" in resp
            assert "checkbox" in resp

            r = client.patch(
                "/api/v1/users/me", json={"fields": [{"field_id": 1, "value": False},]},
            )
            assert r.status_code == 200
            assert UserFieldEntries.query.count() == 1
            assert UserFieldEntries.query.filter_by(id=1).first().value is False
    destroy_ctfd(app)
