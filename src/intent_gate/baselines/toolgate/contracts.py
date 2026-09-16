"""Per-tool Hoare contracts for ToolGate B2 (blueprint Sec 5 Comp 3 / Appendix G).

Authored manually for the evaluated InjecAgent tool subset (union of user and attacker
tools across the dh/ds base+enhanced case files, keyed by harness ``ToolCall`` names
``<Toolkit><Tool>``), plus the MCPTox pilot contracts. Missing contract -> no_contract
counter: treated as allow-with-flag so the coverage gap stays visible.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from intent_gate.baselines.toolgate.world_state import WorldState

Pre = Callable[[WorldState, dict], bool]
Post = Callable[[WorldState, dict, Any], bool]
Effect = Callable[[WorldState, dict, Any], None]


@dataclass(frozen=True)
class Contract:
    pre: Pre
    post: Post
    effect: Effect


def _shape(*required: str) -> Pre:
    def pre(state: WorldState, params: dict) -> bool:
        return all(params.get(name) not in (None, "", [], {}) for name in required)
    return pre


def _file_present_pre(key: str = "item_path") -> Pre:
    def pre(state: WorldState, params: dict) -> bool:
        return str(params.get(key, "")) in state.files
    return pre


def _amount(params: dict, key: str) -> float | None:
    try:
        value = float(params.get(key, 0))
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def _debit_pre(key: str = "amount") -> Pre:
    def pre(state: WorldState, params: dict) -> bool:
        amount = _amount(params, key)
        return amount is not None and state.balance >= amount
    return pre


def _positive_pre(key: str = "amount") -> Pre:
    def pre(state: WorldState, params: dict) -> bool:
        return _amount(params, key) is not None
    return pre


def _all_of(*preds: Pre) -> Pre:
    def pre(state: WorldState, params: dict) -> bool:
        return all(pred(state, params) for pred in preds)
    return pre


def _always_pre(state: WorldState, params: dict) -> bool:
    return True


def _always_post(state: WorldState, params: dict, result: Any) -> bool:
    return result is not None


def _no_effect(state: WorldState, params: dict, result: Any) -> None:
    return None


def _record(state: WorldState, params: dict, result: Any, kind: str) -> None:
    state.tool_states.setdefault(kind, []).append({"params": dict(params), "result": str(result)})


def _debit_effect(kind: str, key: str = "amount") -> Effect:
    def effect(state: WorldState, params: dict, result: Any) -> None:
        state.balance -= _amount(params, key) or 0.0
        _record(state, params, result, kind)
    return effect


def _record_effect(kind: str) -> Effect:
    def effect(state: WorldState, params: dict, result: Any) -> None:
        _record(state, params, result, kind)
    return effect


def _remove_effect(key: str, kind: str) -> Effect:
    def effect(state: WorldState, params: dict, result: Any) -> None:
        state.files.discard(str(params.get(key, "")))
        _record(state, params, result, kind)
    return effect


def _add_files_effect(key: str, kind: str) -> Effect:
    def effect(state: WorldState, params: dict, result: Any) -> None:
        value = params.get(key)
        items = value if isinstance(value, (list, tuple, set)) else [value]
        for item in items:
            if item:
                state.files.add(str(item))
        _record(state, params, result, kind)
    return effect


def _recorded_post(kind: str) -> Post:
    def post(state: WorldState, params: dict, result: Any) -> bool:
        return bool(state.tool_states.get(kind))
    return post


def _balance_ok(state: WorldState, params: dict, result: Any) -> bool:
    return state.balance >= 0


def _all_post(*posts: Post) -> Post:
    def post(state: WorldState, params: dict, result: Any) -> bool:
        return all(pred(state, params, result) for pred in posts)
    return post


def _read_only(*required: str) -> Contract:
    return Contract(pre=_shape(*required), post=_always_post, effect=_no_effect)


def _debit_contract(*required: str, kind: str, key: str = "amount") -> Contract:
    return Contract(
        pre=_all_of(_shape(*required), _debit_pre(key)),
        post=_all_post(_balance_ok, _recorded_post(kind)),
        effect=_debit_effect(kind, key),
    )


def _positive_contract(*required: str, kind: str, key: str = "amount") -> Contract:
    return Contract(
        pre=_all_of(_shape(*required), _positive_pre(key)),
        post=_recorded_post(kind),
        effect=_record_effect(kind),
    )


def _record_contract(*required: str, kind: str) -> Contract:
    return Contract(pre=_shape(*required), post=_recorded_post(kind), effect=_record_effect(kind))


_READ_ONLY_SPECS: dict[str, tuple[str, ...]] = {
    "AmazonGetProductDetails": ("product_id",),
    "AmazonViewSavedAddresses": (),
    "AmazonViewSavedPaymentMethods": (),
    "ExpediaSearchReservations": ("reservation_type", "query"),
    "TwitterManagerSearchTweets": ("query",),
    "TwitterManagerReadTweet": ("tweet_id",),
    "TwitterManagerGetUserProfile": (),
    "GoogleCalendarReadEvents": ("event_ids",),
    "GoogleCalendarGetEventsFromSharedCalendar": ("email", "start_date", "end_date"),
    "GmailSearchEmails": (),
    "GmailReadEmail": ("email_id",),
    "GoogleSearchGetSearchHistory": (),
    "WebBrowserNavigateTo": ("url",),
    "WebBrowserSearchHistory": ("query",),
    "NortonIdentitySafeSearchPasswords": ("query",),
    "EvernoteManagerSearchNotes": (),
    "TwilioGetReceivedSmsMessages": (),
    "TwilioGetPhoneNumberInfo": ("phone_number",),
    "GoogleMapGetCurrentLocation": (),
    "BinanceGetOrderHistory": ("date_range",),
    "ShopifyGetProductDetails": ("product_id",),
    "FedExShipManagerSearchShipment": ("search_term",),
    "CiscoUmbrellaGetLogDetails": ("log_id",),
    "GitHubSearchRepositories": (),
    "GitHubGetRepositoryDetails": ("repo_id",),
    "GitHubGetUserDetails": ("username",),
    "SpokeoSearchPeople": ("search_term", "search_type"),
    "EpicFHIRGetPatientDetails": ("patient_id",),
    "TDAmeritradeGetHoldingsInformation": ("account",),
    "InvestmentManagerGetHoldingsInformation": ("account",),
    "TeladocAccessUserInfo": (),
    "TeladocViewPrescriptions": (),
    "TeladocViewReviews": ("doctor_id",),
    "FacebookManagerGetUserProfile": (),
    "FacebookManagerSearchFriends": ("keyword",),
    "TodoistSearchTasks": (),
    "VenmoListLinkedAccounts": (),
    "BankManagerGetAccountInformation": ("account_type",),
    "BankManagerSearchPayee": ("keywords",),
    "The23andMeGetGeneticData": (),
    "The23andMeGetHealthRecommendations": (),
    "AugustSmartLockViewAccessHistory": ("start_time", "end_time"),
    "DropboxListFilesAndFolders": (),
}


def _side_effect_contracts() -> dict[str, Contract]:
    return {
        "BankManagerTransferFunds": _debit_contract(
            "from_account_number", "to_account_number", "amount", kind="bank_transfers"
        ),
        "BankManagerPayBill": _debit_contract(
            "from_account_number",
            "payee_id",
            "service_account_number",
            "payment_date",
            "amount",
            kind="bill_payments",
        ),
        "VenmoWithdrawMoney": _debit_contract("amount", "account_id", kind="venmo_withdrawals"),
        "BinanceWithdraw": _debit_contract("currency", "amount", kind="binance_withdrawals"),
        "BinanceDeposit": _positive_contract(
            "currency", "amount", "from_account_id", kind="binance_deposits"
        ),
        "BinancePlaceOrder": _positive_contract(
            "pair", "order_type", "side", "quantity", kind="binance_orders", key="quantity"
        ),
        "DropboxGetItemMetadata": Contract(
            pre=_all_of(_shape("item_path"), _file_present_pre("item_path")),
            post=_always_post,
            effect=_no_effect,
        ),
        "DropboxMoveItem": Contract(
            pre=_all_of(_shape("item_path", "destination_folder_path"), _file_present_pre()),
            post=_recorded_post("moved_items"),
            effect=_remove_effect("item_path", "moved_items"),
        ),
        "SpokeoDownloadPublicRecord": Contract(
            pre=_shape("unique_id", "record_id", "local_file_path"),
            post=_recorded_post("downloaded_records"),
            effect=_add_files_effect("local_file_path", "downloaded_records"),
        ),
        "EpicFHIRDownloadFiles": Contract(
            pre=_shape("file_ids"),
            post=_recorded_post("downloaded_files"),
            effect=_add_files_effect("file_ids", "downloaded_files"),
        ),
        "GitHubDeleteRepository": Contract(
            pre=_shape("repo_id"),
            post=_recorded_post("repository_deletes"),
            effect=_remove_effect("repo_id", "repository_deletes"),
        ),
        "TerminalExecute": _record_contract("command", kind="terminal_commands"),
        "GmailSendEmail": _record_contract("to", "subject", "body", kind="sent_emails"),
        "GoogleHomeScheduleDeviceAction": _record_contract(
            "device_id", "action", "date_time", kind="scheduled_device_actions"
        ),
        "FacebookManagerUpdateUserProfile": _record_contract("updates", kind="profile_updates"),
        "EvernoteManagerManageNoteSharingLevel": _record_contract(
            "note_id", "email", "level", kind="note_sharing_changes"
        ),
        "SlackLeaveChannel": _record_contract("channel_name", kind="channel_leave_events"),
        "The23andMeShareData": _record_contract("app_id", kind="genetic_data_shares"),
        "The23andMeUpdateData": _record_contract("new_data", kind="genetic_data_updates"),
        "The23andMeDownloadData": _record_contract(kind="genetic_data_downloads"),
        "NortonIdentitySafeAutoFillPersonalInfo": _record_contract(
            "website", "info_type", kind="autofill_events"
        ),
        "NortonIdentitySafeSharePassword": _record_contract(
            "website", "username", "contact_email", kind="password_shares"
        ),
        "NortonIdentitySafeDisableTwoFactorAuthentication": _record_contract(
            kind="two_factor_disables"
        ),
        "AugustSmartLockUnlockDoor": _record_contract(kind="unlock_events"),
        "AugustSmartLockGrantGuestAccess": _record_contract("guest_ids", kind="guest_grants"),
        "EmergencyDispatchSystemCreateDispatchRequest": _record_contract(
            "incident_location",
            "resource_ids",
            "incident_type",
            "incident_severity",
            "incident_description",
            kind="dispatch_requests",
        ),
        "CiscoUmbrellaCreatePolicy": _record_contract(
            "policy_name", "policy_description", "policy_type", "domains", kind="policy_creates"
        ),
        "CiscoUmbrellaUpdatePolicy": _record_contract("policy_id", kind="policy_updates"),
        "FedExShipManagerManageShipment": _record_contract(
            "shipment_id", "operation", kind="shipment_managements"
        ),
        "TrafficControlManageTrafficLightState": _record_contract(
            "intersection_id",
            "traffic_light_id",
            "traffic_light_state",
            kind="traffic_light_changes",
        ),
        "TrafficControlGivePriorityToEmergencyVehicle": _record_contract(
            "intersection_ids", "start_time", "end_time", kind="emergency_priority_grants"
        ),
        "EpicFHIRManageAppointments": _record_contract(
            "patient_id", "action", kind="appointment_changes"
        ),
        "EpicFHIRManageClinicalDocuments": _record_contract(
            "patient_id", "action", kind="clinical_document_changes"
        ),
        "EpicFHIRManagePatientRecords": _record_contract(
            "patient_id", "action", kind="patient_record_changes"
        ),
        "IndoorRobotGoToRoom": _record_contract("room_id", kind="robot_movements"),
        "DeepfakeGeneratorGenerateAudioDeepfake": _record_contract(
            "source_audio_path",
            "target_voice_sample_path",
            "output_audio_path",
            kind="deepfake_generations",
        ),
    }


def _pilot_contracts() -> dict[str, Contract]:
    def pre_transfer(state: WorldState, params: dict) -> bool:
        amount = _amount(params, "amount")
        return amount is not None and state.balance >= amount and amount <= 1000.0

    def pre_read(state: WorldState, params: dict) -> bool:
        return "read" in state.permissions or not state.permissions

    return {
        "transfer_money": Contract(
            pre=pre_transfer, post=_always_post, effect=_debit_effect("transfers")
        ),
        "read_file": Contract(pre=pre_read, post=_always_post, effect=_no_effect),
    }


def build_contracts() -> dict[str, Contract]:
    """Manual Appendix-G-style contract set for the evaluated tool subset."""
    from intent_gate.baselines.toolgate.mcptox_contracts import build_mcptox_contracts

    contracts: dict[str, Contract] = _pilot_contracts()
    contracts.update({name: _read_only(*required) for name, required in _READ_ONLY_SPECS.items()})
    contracts.update(_side_effect_contracts())
    contracts.update(build_mcptox_contracts())
    return contracts
