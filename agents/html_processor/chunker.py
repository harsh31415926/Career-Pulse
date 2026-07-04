# Get the necessary info from the clean html text

def chunk_size(text , chunk_size = 8000):

    chunks = []

    for i in range(0 , len(text) , chunk_size):
        chunks.append(text[i:i+chunk_size])
    
    return chunks 

