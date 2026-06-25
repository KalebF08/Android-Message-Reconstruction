import sqlite3
import os

conn = sqlite3.connect('mmssms.db')
cursor = conn.cursor()

cursor.execute("""
               SELECT *, datetime(date/1000, 'UNIXEPOCH') AS date_u,
               datetime(date_sent/1000, 'UNIXEPOCH') AS date_sent_u FROM (
                   SELECT thread_id, address, date, date_sent, body FROM sms UNION ALL
                   SELECT pdu.thread_id, addr.address, (date*1000) AS date, (pdu.date_sent*1000) AS date_sent,
                   CASE
                       WHEN part.text is NOT NULL THEN part.text
                       ELSE '[' || part.ct || ']'
                   END AS body FROM pdu
                   INNER JOIN part ON part.mid = pdu._id AND part.ct != 'application/smil'
                   INNER JOIN addr ON addr.msg_id = pdu._id AND addr.type = 137
               ) ORDER BY thread_id, date
               """)
               
query = cursor.fetchall()

message_threads = {}

if not os.path.exists("Message Threads"):
    os.makedirs("Message Threads")

for thread_id, address, date, date_sent, body, date_u, date_sent_u in query:
    if thread_id not in message_threads:
        message_threads[thread_id] = []
    
    if date_sent != 0:
        date = date_sent_u
    else:
        date = date_u
    
    message_threads[thread_id].append((date, address, body))

for thread_id, messages in message_threads.items():
    filename = f"Message Threads/Thread_{thread_id}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Thread {thread_id}\n\n")
        
        for date, address, body in messages:
            f.write(f"[{date}] {address}: {body}\n")

conn.close()