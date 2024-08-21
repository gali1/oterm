import json
import logging
from typing import Optional, Dict

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TabbedContent, TabPane

from oterm.app.chat_edit import ChatEdit
from oterm.app.splash import SplashScreen
from oterm.app.widgets.chat import ChatContainer
from oterm.config import appConfig
from oterm.store.store import Store

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OTerm(App):
    TITLE = "oTerm"
    SUB_TITLE = "A terminal-based Ollama client."
    CSS_PATH = "oterm.tcss"
    BINDINGS = [
        ("ctrl+n", "new_chat", "new"),
        ("ctrl+tab", "cycle_chat(+1)", "next chat"),
        ("ctrl+shift+tab", "cycle_chat(-1)", "prev chat"),
        ("ctrl+t", "toggle_dark", "toggle theme"),
        ("ctrl+q", "quit", "quit"),
    ]

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark
        appConfig.set("theme", "dark" if self.dark else "light")
        logging.info(f"Theme set to {'dark' if self.dark else 'light'}")

    async def action_quit(self) -> None:
        logging.info("Quitting the application")
        await self.exit()

    async def action_cycle_chat(self, change: int) -> None:
        tabs = self.query_one(TabbedContent)
        saved_chats = await self.store.get_chats()
        if tabs.active_pane is None:
            return
        active_id = int(str(tabs.active_pane.id).split("-")[1])
        for _chat in saved_chats:
            if _chat[0] == active_id:
                next_index = (saved_chats.index(_chat) + change) % len(saved_chats)
                next_id = saved_chats[next_index][0]
                tabs.active = f"chat-{next_id}"
                logging.info(f"Switched to chat {next_id}")
                break

    def action_new_chat(self) -> None:
        async def on_model_select(model_info: Optional[str]) -> None:
            if model_info is None:
                return
            try:
                model: Dict = json.loads(model_info)
                tabs = self.query_one(TabbedContent)
                tab_count = tabs.tab_count
                name = f"chat #{tab_count+1} - {model['name']}"
                id = await self.store.save_chat(
                    id=None,
                    name=name,
                    model=model["name"],
                    system=model["system"],
                    format=model["format"],
                    parameters=json.dumps(model["parameters"]),
                    keep_alive=model["keep_alive"],
                )
                pane = TabPane(name, id=f"chat-{id}")
                pane.compose_add_child(
                    ChatContainer(
                        db_id=id,
                        chat_name=name,
                        model=model["name"],
                        system=model["system"],
                        format=model["format"],
                        parameters=model["parameters"],
                        keep_alive=model["keep_alive"],
                        messages=[],
                    )
                )
                await tabs.add_pane(pane)
                tabs.active = f"chat-{id}"
                logging.info(f"Created new chat {name} with ID {id}")

            except json.JSONDecodeError as e:
                logging.error(f"Error parsing model info: {e}")
            except Exception as e:
                logging.error(f"Error during new chat creation: {e}")

        self.push_screen(ChatEdit(), on_model_select)

    async def on_mount(self) -> None:
        self.store = await Store.create()
        self.dark = appConfig.get("theme") == "dark"
        saved_chats = await self.store.get_chats()
        if not saved_chats:
            self.action_new_chat()
        else:
            tabs = self.query_one(TabbedContent)
            for id, name, model, system, format, parameters, keep_alive in saved_chats:
                try:
                    messages = await self.store.get_messages(id)
                    container = ChatContainer(
                        db_id=id,
                        chat_name=name,
                        model=model,
                        messages=messages,
                        system=system,
                        format=format,
                        parameters=parameters,
                        keep_alive=keep_alive,
                    )
                    pane = TabPane(name, container, id=f"chat-{id}")
                    tabs.add_pane(pane)
                except Exception as e:
                    logging.error(f"Error loading chat {id}: {e}")
        await self.push_screen(SplashScreen())

    @on(TabbedContent.TabActivated)
    async def on_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        container = event.pane.query_one(ChatContainer)
        try:
            await container.load_messages()
            logging.info(f"Loaded messages for tab {event.pane.id}")
        except Exception as e:
            logging.error(f"Error loading messages for tab {event.pane.id}: {e}")

    def compose(self) -> ComposeResult:
        yield Header()
        yield TabbedContent(id="tabs")
        yield Footer()


app = OTerm()
