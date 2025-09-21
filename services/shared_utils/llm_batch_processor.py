import asyncio
import logging

logger = logging.getLogger(__name__)

async def llm_ainvoke_batch(llm_chain, professor_info_list, max_concurrent=5):
    """
    Process multiple LLM calls concurrently with rate limiting.
    
    Args:
        llm_chain: The LLM chain to use
        professor_info_list: List of CrawlerResult objects with .markdown and .url attributes
        max_concurrent: Maximum number of concurrent LLM calls
    
    Returns:
        List of processed results
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_single(markdown, url):
        async with semaphore:
            try:
                logger.info(f"invoking llm for {url}")
                data = await llm_chain.ainvoke({"markdown": markdown, "src_url": url})
                return data, None
            except Exception as e:
                logger.error(f"LLM error while extracting info from {url}: {e}")
                return None, e
    
    # Create tasks for all LLM calls
    tasks = []
    for professor_info in professor_info_list:
        markdown = getattr(professor_info, "markdown")
        src_url = getattr(professor_info, "url")
        if markdown and src_url:
            tasks.append(process_single(markdown, src_url))
        else:
            logger.warning(f"Skipping professor. No markdown or url found.")
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results and maintain order
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Task failed with exception: {result}")
            continue
            
        data, error = result
        if data and not error:
            professor_data = data.model_dump()
            if professor_data:
                processed_results.append(professor_data)
    
    return processed_results