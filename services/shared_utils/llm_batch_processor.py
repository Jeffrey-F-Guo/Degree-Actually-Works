import asyncio
import logging

logger = logging.getLogger(__name__)

async def llm_ainvoke_batch(llm_chain, markdown_list, url_list, max_concurrent=5):
    """
    Process multiple LLM calls concurrently with rate limiting.
    
    Args:
        llm_chain: The LLM chain to use
        markdown_list: List of markdown content to process
        url_list: List of corresponding URLs for logging
        max_concurrent: Maximum number of concurrent LLM calls
    
    Returns:
        List of processed results
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_single(markdown, url):
        async with semaphore:
            try:
                logger.info(f"invoking llm for {url}")
                data = await llm_chain.ainvoke({"markdown": markdown})
                return data, url, None
            except Exception as e:
                logger.error(f"LLM error while extracting info from {url}: {e}")
                return None, url, e
    
    # Create tasks for all LLM calls
    tasks = [
        process_single(markdown, url) 
        for (markdown, url) in zip(markdown_list, url_list)
        if markdown  # Only process non-empty markdown
    ]
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results and maintain order
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Task failed with exception: {result}")
            continue
            
        data, url, error = result
        if data and not error:
            professor_data = data.model_dump()
            if professor_data:
                professor_data["src_url"] = url
                processed_results.append(professor_data)
    
    return processed_results