"""Pluggy Connect onboarding page — lets users link their bank account in-app."""
from __future__ import annotations

import re
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from app.components.styles import page_header

# Pluggy Bank sandbox connector ID
_SANDBOX_CONNECTOR_ID = 2


def _get_pluggy_client():
    from src.config import settings
    from src.mcp.pluggy_direct import PluggyDirectClient
    return PluggyDirectClient(
        client_id=settings.PLUGGY_CLIENT_ID,
        client_secret=settings.PLUGGY_CLIENT_SECRET,
        item_id=None,
        base_url=settings.PLUGGY_BASE_URL,
    )


def _save_item_id_to_env(item_id: str) -> None:
    """Persist the item_id into the .env file."""
    env_path = Path(__file__).parent.parent.parent / ".env"
    content = env_path.read_text(encoding="utf-8")
    if re.search(r"^PLUGGY_ITEM_ID=.*$", content, re.MULTILINE):
        content = re.sub(
            r"^(PLUGGY_ITEM_ID=).*$",
            f"PLUGGY_ITEM_ID={item_id}",
            content,
            flags=re.MULTILINE,
        )
    else:
        content += f"\nPLUGGY_ITEM_ID={item_id}\n"
    env_path.write_text(content, encoding="utf-8")
    import importlib
    import src.config
    importlib.reload(src.config)


def _create_sandbox_item() -> str:
    """Create a Pluggy sandbox item via API and return its item_id."""
    import httpx
    from src.config import settings

    resp = httpx.post(
        f"{settings.PLUGGY_BASE_URL}/auth",
        json={"clientId": settings.PLUGGY_CLIENT_ID, "clientSecret": settings.PLUGGY_CLIENT_SECRET},
        timeout=15,
    )
    resp.raise_for_status()
    api_key = resp.json()["apiKey"]
    headers = {"X-API-KEY": api_key}

    r = httpx.post(
        f"{settings.PLUGGY_BASE_URL}/items",
        json={
            "connectorId": _SANDBOX_CONNECTOR_ID,
            "parameters": {"user": "user-ok", "password": "password-ok"},
        },
        headers=headers,
        timeout=30,
    )
    if r.status_code == 400 and "ITEM_USER_ALREADY_EXISTS" in r.text:
        import json
        existing_ids = r.json().get("items", [])
        if existing_ids:
            return existing_ids[0]
        raise RuntimeError("Item already exists but ID not returned.")
    r.raise_for_status()
    return r.json()["id"]


def _poll_item_status(item_id: str, max_wait: int = 30) -> str:
    """Poll until item sync completes. Returns executionStatus."""
    import httpx
    from src.config import settings

    resp = httpx.post(
        f"{settings.PLUGGY_BASE_URL}/auth",
        json={"clientId": settings.PLUGGY_CLIENT_ID, "clientSecret": settings.PLUGGY_CLIENT_SECRET},
        timeout=15,
    )
    api_key = resp.json()["apiKey"]
    headers = {"X-API-KEY": api_key}

    for _ in range(max_wait // 3):
        r = httpx.get(f"{settings.PLUGGY_BASE_URL}/items/{item_id}", headers=headers, timeout=10)
        data = r.json()
        status = data.get("executionStatus", "")
        if status in ("SUCCESS", "ERROR", "MERGE_ERROR", "PARTIAL_SUCCESS"):
            return status
        time.sleep(3)
    return "TIMEOUT"


def render_connect_page() -> None:
    page_header("Conectar Banco", "Vincule sua conta bancária via Open Finance Brasil")

    from src.config import settings

    # ── Already connected ──────────────────────────────────────────────────
    if settings.PLUGGY_ITEM_ID:
        st.markdown(f"""
        <div class="card-elevated fade-in" style="border-left:4px solid var(--success);padding:1.25rem 1.5rem;">
            <div style="font-size:0.92rem;font-weight:600;color:var(--success);margin-bottom:0.3rem;">
                Conta conectada
            </div>
            <div style="font-size:0.8rem;color:var(--text-muted);font-family:monospace;">
                Item ID: {settings.PLUGGY_ITEM_ID}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Desconectar", type="secondary", icon=":material/link_off:"):
                _save_item_id_to_env("")
                st.session_state.pop("_pluggy_warn_shown", None)
                st.cache_data.clear()
                st.rerun()
        with col2:
            if st.button("Reconectar outro banco", type="secondary", icon=":material/refresh:"):
                _save_item_id_to_env("")
                st.session_state.pop("_pluggy_warn_shown", None)
                st.session_state.pop("connect_token", None)
                st.cache_data.clear()
                st.rerun()
        return

    # ── Two connection paths ───────────────────────────────────────────────
    tab_sandbox, tab_widget = st.tabs(["Sandbox (teste)", "Banco real (Connect Widget)"])

    # ── Tab 1: one-click sandbox ───────────────────────────────────────────
    with tab_sandbox:
        st.markdown("""
        <div class="card-elevated" style="margin-bottom:1rem;">
            <div style="font-size:0.88rem;color:var(--text-secondary);line-height:1.6;">
                Cria uma conexão de teste com dados sintéticos do <strong>Pluggy Bank</strong>
                (conector sandbox, sem credenciais reais).
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.info(
            "**Credenciais sandbox:** `user-ok` / `password-ok`  \n"
            "Connector ID: `2` (Pluggy Bank) — dados sintéticos, sem vínculo com banco real."
        )

        if st.button("Criar conexão sandbox", type="primary", icon=":material/bolt:"):
            with st.spinner("Criando item sandbox no Pluggy..."):
                try:
                    item_id = _create_sandbox_item()
                    st.info(f"Item criado: `{item_id}` — aguardando sincronização...")
                    status = _poll_item_status(item_id)
                    if status == "SUCCESS":
                        _save_item_id_to_env(item_id)
                        st.session_state.pop("_pluggy_warn_shown", None)
                        st.cache_data.clear()
                        st.success(f"Conectado! Item ID: `{item_id}`")
                        st.balloons()
                        st.rerun()
                    else:
                        st.warning(f"Item criado mas sync retornou: `{status}`. Item ID: `{item_id}`")
                        _save_item_id_to_env(item_id)
                        st.cache_data.clear()
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Tab 2: real bank via Connect Widget ───────────────────────────────
    with tab_widget:
        st.markdown("""
        <div class="card-elevated" style="margin-bottom:1rem;">
            <div style="font-size:0.88rem;color:var(--text-secondary);line-height:1.6;">
                Conecte seu banco real via <strong>Open Finance Brasil</strong>.
                O widget do Pluggy abre dentro do app.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if "connect_token" not in st.session_state:
            if st.button("Abrir widget de conexão", type="primary", icon=":material/account_balance:"):
                with st.spinner("Gerando token de acesso..."):
                    try:
                        client = _get_pluggy_client()
                        token = client.create_connect_token()
                        st.session_state.connect_token = token
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao gerar token: {e}")
        else:
            connect_token = st.session_state.connect_token

            widget_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8">
              <style>
                body {{ margin: 0; background: #f8fafc; font-family: 'Inter', sans-serif; }}
                #status {{
                  padding: 0.75rem 1rem; color: #475569; font-size: 0.85rem;
                  background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin: 0.5rem;
                }}
                #item-id-box {{
                  display: none; padding: 0.75rem 1rem; background: rgba(16,185,129,0.08);
                  border: 1px solid #10b981; border-radius: 10px; color: #059669;
                  font-size: 0.9rem; font-family: monospace; margin: 0.5rem;
                  word-break: break-all;
                }}
              </style>
            </head>
            <body>
              <div id="status">Carregando widget do Pluggy...</div>
              <div id="item-id-box"></div>
              <script src="https://cdn.pluggy.ai/connect/v2/pluggy-connect.js"></script>
              <script>
                const pluggyConnect = new window.PluggyConnect({{
                  connectToken: "{connect_token}",
                  includeSandbox: true,
                  onSuccess: function(itemData) {{
                    const itemId = itemData.item.id;
                    document.getElementById('status').textContent = 'Conectado! Copie o Item ID abaixo:';
                    document.getElementById('item-id-box').style.display = 'block';
                    document.getElementById('item-id-box').textContent = itemId;
                    window.parent.postMessage({{ type: 'pluggy_item_id', itemId: itemId }}, '*');
                  }},
                  onError: function(e) {{
                    document.getElementById('status').textContent = 'Erro: ' + e.message;
                  }},
                  onClose: function() {{
                    document.getElementById('status').textContent = 'Widget fechado. Cole o Item ID abaixo.';
                  }}
                }});
                pluggyConnect.init();
                document.getElementById('status').textContent = 'Widget pronto. Selecione seu banco.';
              </script>
            </body>
            </html>
            """

            components.html(widget_html, height=540, scrolling=False)

            st.divider()
            col1, col2 = st.columns([3, 1])
            with col1:
                manual_id = st.text_input(
                    "Item ID",
                    placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                    help="Exibido no widget após conexão bem-sucedida.",
                )
            with col2:
                st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
                if st.button("Salvar", type="primary", disabled=not manual_id, icon=":material/check:"):
                    _save_item_id_to_env(manual_id.strip())
                    st.session_state.pop("connect_token", None)
                    st.session_state.pop("_pluggy_warn_shown", None)
                    st.cache_data.clear()
                    st.success("Item ID salvo!")
                    st.balloons()
                    st.rerun()

            if st.button("Cancelar", type="secondary", icon=":material/arrow_back:"):
                st.session_state.pop("connect_token", None)
                st.rerun()
