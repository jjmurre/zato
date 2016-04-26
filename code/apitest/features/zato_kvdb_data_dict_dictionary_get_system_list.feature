@kvdb.data-dict
Feature: kvdb.data.dict.dictionary.get-system-list
  Returns a list of systems defined in a KVDB.

  @kvdb.data-dict.dictionary.get-system-list
  Scenario: Set up

    Given I store a random string under "first_test_system"
    Given I store a random string under "first_test_key"
    Given I store a random string under "second_test_system"
    Given I store a random string under "second_test_key"
    Given I store a random string under "test_value"

  @kvdb.data-dict.dictionary.get-system-list
  Scenario: Create data dictionary test entry in a cluster's KVDB

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.kvdb.data-dict.dictionary.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/system" in request is "#first_test_system"
    Given JSON Pointer "/key" in request is "#first_test_key"
    Given JSON Pointer "/value" in request is "#test_value"

    When the URL is invoked

    Then JSON Pointer "/zato_env/result" is "ZATO_OK"
    And I store "/zato_kvdb_data_dict_dictionary_create_response/id" from response under "first_dictionary_entry_id"

  @kvdb.data-dict.dictionary.get-system-list
  Scenario: Create another data dictionary test entry in a cluster's KVDB

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.kvdb.data-dict.dictionary.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/system" in request is "#second_test_system"
    Given JSON Pointer "/key" in request is "#second_test_key"
    Given JSON Pointer "/value" in request is "#test_value"

    When the URL is invoked

    Then JSON Pointer "/zato_env/result" is "ZATO_OK"
    And I store "/zato_kvdb_data_dict_dictionary_create_response/id" from response under "second_dictionary_entry_id"

  @kvdb.data-dict.dictionary.get-system-list
  Scenario: Invoke get-system-list to get the at least the 2 systems we just defined

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.kvdb.data-dict.dictionary.get-system-list"

    When the URL is invoked

    Then JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_kvdb_data_dict_dictionary_get_system_list_response" isn't an empty list

  @kvdb.data-dict.dictionary.get-system-list
  Scenario: Delete first dictionary entry

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.kvdb.data-dict.dictionary.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#first_dictionary_entry_id"

    When the URL is invoked

    Then JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_kvdb_data_dict_dictionary_delete_response/id" is an integer "#first_dictionary_entry_id"

  @kvdb.data-dict.dictionary.get-system-list
  Scenario: Delete second dictionary entry

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.kvdb.data-dict.dictionary.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#second_dictionary_entry_id"

    When the URL is invoked

    Then JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_kvdb_data_dict_dictionary_delete_response/id" is an integer "#second_dictionary_entry_id"
