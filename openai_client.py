import asyncio
import base64
from openai import AsyncOpenAI
from config import Config

class OpenAIClient:
    def __init__(self):
        # v2 API үшін дұрыс инициализация
        self.client = AsyncOpenAI(
            api_key=Config.OPENAI_API_KEY
        )
        self.assistant_id = Config.OPENAI_ASSISTANT_ID
        self.vector_store_id = Config.VECTOR_STORE_ID
    
    async def create_thread(self):
        """Жаңа thread жасау"""
        try:
            # v2 API header-мен
            thread = await self.client.beta.threads.create(
                extra_headers={"OpenAI-Beta": "assistants=v2"}
            )
            print(f"✅ Thread жасалды: {thread.id}")
            return thread.id
        except Exception as e:
            print(f"❌ Thread жасау қатесі: {e}")
            # Уақытша thread ID қайтару (offline режим)
            return f"temp_thread_{abs(hash(str(e))) % 10000}"
    
    async def send_message(self, thread_id, message, image_base64=None):
        """Хабарлама жіберу"""
        try:
            # Егер temp thread болса, нақты thread жасау
            if thread_id.startswith("temp_thread_"):
                print("🔄 Нақты thread жасап жатырмын...")
                real_thread_id = await self.create_thread()
                if not real_thread_id.startswith("temp_thread_"):
                    thread_id = real_thread_id
                else:
                    return "OpenAI байланысы жоқ. API Key мен Assistant ID тексеріңіз."
            
            # Хабарлама құрамын дайындау
            content = []
            
            if image_base64:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                })
            
            content.append({
                "type": "text",
                "text": message
            })
            
            # Хабарламаны thread-қа қосу (v2 header-мен)
            await self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=content,
                extra_headers={"OpenAI-Beta": "assistants=v2"}
            )
            
            # Run жасау (v2 header-мен)
            run = await self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id,
                extra_headers={"OpenAI-Beta": "assistants=v2"}
            )
            
            # Жауапты күту
            max_attempts = 30  # 30 секунд күту
            attempt = 0
            
            while attempt < max_attempts:
                run_status = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id,
                    extra_headers={"OpenAI-Beta": "assistants=v2"}
                )
                
                if run_status.status == 'completed':
                    break
                elif run_status.status in ['failed', 'cancelled', 'expired']:
                    error_msg = f"Run failed with status: {run_status.status}"
                    if hasattr(run_status, 'last_error') and run_status.last_error:
                        error_msg += f" - {run_status.last_error}"
                    print(f"❌ Run қатесі: {error_msg}")
                    return "Кешіріңіз, сұрақты өңдеуде қате орын алды."
                elif run_status.status == 'requires_action':
                    # Tool calls болса, олармен жұмыс жасау керек
                    print("⚠️ Tool action талап етілуде")
                    await asyncio.sleep(2)
                else:
                    # in_progress, queued статустары
                    await asyncio.sleep(1)
                
                attempt += 1
            
            if attempt >= max_attempts:
                return "Сұрақты өңдеу тым ұзақ уақыт алды. Қайталап көріңіз."
            
            # Жауапты алу (v2 header-мен)
            messages = await self.client.beta.threads.messages.list(
                thread_id=thread_id,
                limit=1,
                extra_headers={"OpenAI-Beta": "assistants=v2"}
            )
            
            if messages.data:
                # Жауапты алу
                content = messages.data[0].content[0]
                if hasattr(content, 'text'):
                    return content.text.value
                else:
                    return str(content)
            else:
                return "Жауап алу мүмкін болмады."
                
        except Exception as e:
            print(f"OpenAI API қатесі: {e}")
            
            # Нақты қате тексеру
            error_str = str(e).lower()
            
            if "assistant" in error_str and ("not found" in error_str or "does not exist" in error_str):
                return "❌ Assistant ID дұрыс емес. OpenAI платформасында Assistant жасап, ID-ды .env файлына қойыңыз."
            
            if "thread" in error_str and ("not found" in error_str or "does not exist" in error_str):
                return "❌ Thread қатесі орын алды. Ботты қайта іске қосыңыз (/start)."
            
            if "unauthorized" in error_str or "api_key" in error_str or "authentication" in error_str:
                return "❌ API key қатесі. OpenAI API key дұрыс емес. .env файлындағы OPENAI_API_KEY тексеріңіз."
            
            if "rate limit" in error_str or "quota" in error_str:
                return "❌ OpenAI лимиті аяқталды. Кейінірек қайталап көріңіз."
            
            if "v1 assistants api has been deprecated" in error_str:
                return "❌ OpenAI кітапханасы ескірген. 'pip install --upgrade openai' команданысын орындаңыз."
            
            return f"Техникалық қате орын алды: {str(e)[:100]}..."
    
    async def test_connection(self):
        """OpenAI байланысын тексеру"""
        try:
            # Assistant алу арқылы байланысты тексеру
            assistant = await self.client.beta.assistants.retrieve(
                assistant_id=self.assistant_id,
                extra_headers={"OpenAI-Beta": "assistants=v2"}
            )
            print(f"✅ Assistant табылды: {assistant.name}")
            return True
        except Exception as e:
            print(f"❌ OpenAI байланысы жоқ: {e}")
            return False
