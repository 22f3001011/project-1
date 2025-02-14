import os
import json
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import httpx
import git
from PIL import Image
import pandas as pd
from bs4 import BeautifulSoup
import markdown

class TaskHandler:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.data_dir = Path("/data")

    async def handle_task(self, task: str) -> Dict[str, Any]:
        """Main task dispatcher"""
        # Use LLM to classify the task and extract parameters
        classification = await self._classify_task(task)
        
        task_type = classification['task_type']
        params = classification['parameters']
        
        # Map task types to handler methods
        handlers = {
            'install_uv': self._handle_uv_installation,
            'format_markdown': self._handle_markdown_formatting,
            'count_weekdays': self._handle_weekday_counting,
            'sort_contacts': self._handle_contact_sorting,
            'recent_logs': self._handle_recent_logs,
            'create_index': self._handle_markdown_index,
            'extract_email': self._handle_email_extraction,
            'extract_card': self._handle_card_extraction,
            'find_similar': self._handle_similar_comments,
            'query_database': self._handle_database_query,
            'fetch_api': self._handle_api_fetch,
            'git_operations': self._handle_git_ops,
            'scrape_website': self._handle_web_scraping,
            'process_image': self._handle_image_processing,
            'process_audio': self._handle_audio_processing,
            'convert_markdown': self._handle_markdown_conversion,
            'filter_csv': self._handle_csv_filtering
        }
        
        handler = handlers.get(task_type)
        if not handler:
            raise ValueError(f"Unknown task type: {task_type}")
            
        return await handler(params)

    async def _classify_task(self, task: str) -> Dict[str, Any]:
        """Use LLM to classify task and extract parameters"""
        prompt = f"""
        Classify the following task and extract relevant parameters:
        {task}
        
        Return a JSON with:
        - task_type: one of [install_uv, format_markdown, count_weekdays, ...]
        - parameters: dictionary of relevant parameters
        """
        
        response = await self.llm_client.get_completion(prompt)
        return json.loads(response)

    # Phase A Task Handlers

    async def _handle_uv_installation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """A1: Install uv and run datagen script"""
        try:
            # Install uv if not present
            subprocess.run(['curl', '-LsSf', 'https://astral.sh/uv/install.sh'], check=True)
            
            # Run datagen script with email
            script_url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
            subprocess.run(['wget', script_url], check=True)
            subprocess.run(['python', 'datagen.py', params['email']], check=True)
            
            return {"status": "success"}
        except Exception as e:
            raise Exception(f"Failed to handle uv installation: {str(e)}")

    async def _handle_markdown_formatting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """A2: Format markdown using prettier"""
        try:
            input_file = self.data_dir / "format.md"
            subprocess.run([
                'npx', 'prettier@3.4.2', 
                '--write', str(input_file)
            ], check=True)
            return {"status": "success"}
        except Exception as e:
            raise Exception(f"Failed to format markdown: {str(e)}")

    async def _handle_weekday_counting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """A3: Count specific weekdays in dates file"""
        try:
            dates_file = self.data_dir / "dates.txt"
            output_file = self.data_dir / "dates-wednesdays.txt"
            
            with open(dates_file) as f:
                dates = f.readlines()
            
            count = sum(1 for date in dates 
                       if datetime.strptime(date.strip(), '%Y-%m-%d').weekday() == 2)
            
            with open(output_file, 'w') as f:
                f.write(str(count))
                
            return {"status": "success"}
        except Exception as e:
            raise Exception(f"Failed to count weekdays: {str(e)}")

    async def _handle_contact_sorting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """A4: Sort contacts by last_name, first_name"""
        try:
            input_file = self.data_dir / "contacts.json"
            output_file = self.data_dir / "contacts-sorted.json"
            
            with open(input_file) as f:
                contacts = json.load(f)
            
            sorted_contacts = sorted(
                contacts,
                key=lambda x: (x['last_name'], x['first_name'])
            )
            
            with open(output_file, 'w') as f:
                json.dump(sorted_contacts, f, indent=2)
                
            return {"status": "success"}
        except Exception as e:
            raise Exception(f"Failed to sort contacts: {str(e)}")

    async def _handle_recent_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """A5: Get first lines of recent log files"""
        try:
            logs_dir = self.data_dir / "logs"
            output_file = self.data_dir / "logs-recent.txt"
            
            # Get all .log files sorted by modification time
            log_files = sorted(
                logs_dir.glob("*.log"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:10]
            
            first_lines = []
            for log_file in log_files:
                with open(log_file) as f:
                    first_lines.append(f.readline().strip())
            
            with open(output_file, 'w') as f:
                f.write('\n'.join(first_lines))
                
            return {"status": "success"}
        except Exception as e:
            raise Exception(f"Failed to process log files: {str(e)}")

    async def _handle_markdown_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """A6: Create index of markdown files"""
        try:
            docs_dir = self.data_dir / "docs"
            output_file = self.data_dir / "docs/index.json"
            
            index = {}
            for md_file in docs_dir.glob("**/*.md"):
                with open(md_file) as f:
                    content = f.read()
                    # Find first H1 header
                    for line in content.split('\n'):
                        if line.startswith('# '):
                            relative_path = str(md_file.relative_to(docs_dir))
                            index[relative_path] = line[2:].strip()
                            break
            
            with open(output_file, 'w') as f:
                json.dump(index, f, indent=2)
                
            return {"status": "success"}
        except Exception as e:
            raise Exception(f"Failed to create markdown index: {str(e)}")

    async def _handle_email_extraction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """A7: Extract email address using LLM"""
        try:
            input_file = self.data_dir / "email.txt"
            output_file = self.data_dir / "email-sender.txt"
            
            with open(input_file) as f:
                email_content = f.read()
            
            prompt = f"""
            Extract the sender's email address from this email:
            {email_content}
            Return only the email address, nothing else.
            """
            
            email = await self.llm_client.get_completion(prompt)
            
            with open(output_file, 'w') as f:
                f.write(email.strip())
                
            return {"status": "success"}
        except Exception as e:
            raise Exception(f"Failed to extract email: {str(e)}")

    async def _handle_card_extraction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """A8: Extract credit card number using LLM"""
        try:
            input_file = self.data_dir / "credit-card.png"
            output_file = self.data_dir / "credit-card.txt"
            
            # Convert image to base64 for LLM
            with open(input_file, 'rb') as f:
                image_data = f.read()
            
            # Send image to LLM for processing
            response = await self.llm_client.process_image(image_data)
            
            with open(output_file, 'w') as f:
                f.write(response.strip())
                
            return {"status": "success"}
        except Exception as e:
            raise Exception(f"Failed to extract card number: {str(e)}")

    async def _handle_similar_comments(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """A9: Find similar comments using embeddings"""
        try:
            input_file = self.data_dir / "comments.txt"
            output_file = self.data_dir / "comments-similar.txt"
            
            with open(input_file) as f:
                comments = f.read().splitlines()
            
            # Get embeddings for all comments
            embeddings = await self.llm_client.get_embeddings(comments)
            
            # Find most similar pair
            max_similarity = -1
            similar_pair = None
            
            for i in range(len(comments)):
                for j in range(i + 1, len(comments)):
                    similarity = self._cosine_similarity(
                        embeddings[i],
                        embeddings[j]
                    )
                    if similarity > max_similarity:
                        max_similarity = similarity
                        similar_pair = (comments[i], comments[j])
            
            with open(output_file, 'w') as f:
                f.write('\n'.join(similar_pair))
                
            return {"status": "success"}
        except Exception as e:
            raise Exception(f"Failed to find similar comments: {str(e)}")

    async def _handle_database_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """A10: Query SQLite database"""
        try:
            db_file = self.data_dir / "ticket-sales.db"
            output_file = self.data_dir / "ticket-sales-gold.txt"
            
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT SUM(units * price)
                FROM tickets
                WHERE type = 'Gold'
            """)
            
            total = cursor.fetchone()[0]
            conn.close()
            
            with open(output_file, 'w') as f:
                f.write(str(total))
                
            return {"status": "success"}
        except Exception as e:
            raise Exception(f"Failed to query database: {str(e)}")
