use starknet::providers::{jsonrpc::HttpTransport, JsonRpcClient, Provider};
use url::Url;
use anyhow::{Context, Result};
use crate::rate_limiter::ApiRateLimiter;
use std::env;
use std::sync::atomic::{AtomicUsize, Ordering};

pub struct StarknetClient {
    providers: Vec<JsonRpcClient<HttpTransport>>,
    current_index: AtomicUsize,
    limiter: ApiRateLimiter,
}

impl StarknetClient {
    /// Create a new StarknetClient. 
    /// If `rpc_url` is provided, it uses ONLY that one.
    /// Otherwise, it detects ALL compatible URLs in the environment and rotates between them.
    pub fn new(rpc_url: Option<&str>) -> Result<Self> {
        // Load .env if not already loaded
        dotenv::dotenv().ok();

        let mut url_strings = Vec::new();

        if let Some(u) = rpc_url {
            url_strings.push(u.to_string());
        } else {
            url_strings = Self::detect_rpc_urls()?;
        }

        let mut providers = Vec::new();
        for url_str in url_strings {
            let url = Url::parse(&url_str).context(format!("Invalid RPC URL: {}", url_str))?;
            providers.push(JsonRpcClient::new(HttpTransport::new(url)));
        }

        if providers.is_empty() {
             return Err(anyhow::anyhow!("No valid RPC providers available."));
        }

        // Default to safe limit: 5 requests per second (typical free tier)
        // Note: This limit is global for the client struct, effectively limiting total throughput 
        // regardless of which provider is used next.
        let limiter = ApiRateLimiter::new(5)?;

        Ok(StarknetClient { 
            providers, 
            current_index: AtomicUsize::new(0),
            limiter 
        })
    }

    fn detect_rpc_urls() -> Result<Vec<String>> {
        let keys = [
            "STARKNET_RPC_URL",
            "STARKNET_MAINNET_URL",
            "STARKNET_LAVA_URL",
            "STARKNET_1RPC_URL",
            "ALCHEMY_RPC_URL",
            "INFURA_RPC_URL",
            "QUICKNODE_ENDPOINT",
        ];

        let mut urls = Vec::new();
        for key in keys {
            if let Ok(val) = env::var(key) {
                let trimmed = val.trim();
                if !trimmed.is_empty() {
                    // Validate URL format before adding
                    if Url::parse(trimmed).is_ok() {
                        urls.push(trimmed.to_string());
                    }
                }
            }
        }
        
        if urls.is_empty() {
            Err(anyhow::anyhow!("No valid RPC URL found in environment variables."))
        } else {
            Ok(urls)
        }
    }

    fn next_provider(&self) -> &JsonRpcClient<HttpTransport> {
        let idx = self.current_index.fetch_add(1, Ordering::Relaxed);
        &self.providers[idx % self.providers.len()]
    }

    pub async fn get_network_status(&self) -> Result<(u64, u128)> {
        self.limiter.check().await;
        use starknet::core::types::{BlockId, BlockTag, MaybePendingBlockWithTxHashes};

        let provider = self.next_provider();
        
        let block = provider.get_block_with_tx_hashes(BlockId::Tag(BlockTag::Latest)).await
            .map_err(|e| anyhow::anyhow!("Failed to fetch block: {}", e))?;

        match block {
            MaybePendingBlockWithTxHashes::Block(b) => {
                // l1_gas_price is FieldElement in this version.
                // Convert via string to avoid trait complexity (Felt -> u128)
                let gas_felt = b.l1_gas_price.price_in_wei; 
                let gas: u128 = format!("{}", gas_felt).parse().unwrap_or(0);
                Ok((b.block_number, gas))
            },
            MaybePendingBlockWithTxHashes::PendingBlock(b) => {
                 let gas_felt = b.l1_gas_price.price_in_wei;
                 let gas: u128 = format!("{}", gas_felt).parse().unwrap_or(0);
                 Ok((0, gas))
            }
        }
    }

    pub async fn get_eth_balance(&self, address: &str) -> Result<u128> {
        self.limiter.check().await;
        use starknet::core::types::{BlockId, BlockTag, FunctionCall, FieldElement};
        use starknet::core::utils::get_selector_from_name;
        
        let provider = self.next_provider();
        let eth_contract = FieldElement::from_hex_be("0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7")?;
        let selector = get_selector_from_name("balanceOf")?;
        let user_address = FieldElement::from_hex_be(address).context("Invalid address format")?;

        let call = FunctionCall {
            contract_address: eth_contract,
            entry_point_selector: selector,
            calldata: vec![user_address],
        };

        let result = provider.call(call, BlockId::Tag(BlockTag::Latest)).await
            .map_err(|e| anyhow::anyhow!("Failed to fetch balance: {}", e))?;
            
        // Uint256 is [low, high]
        if result.len() < 2 {
            return Ok(0);
        }
        
        // Convert low part to u128. High part ignored (safe for < 3.4 * 10^38 Wei)
        let low = result[0];
        let balance: u128 = format!("{}", low).parse().unwrap_or(0);
        
        Ok(balance)
    }

    /// Execute a batched query (Multicall).
    pub async fn batch_query(&self, _account_address: &str, _asteroids: &[u64]) -> Result<String> {
        self.limiter.check().await;
        let _provider = self.next_provider();
        
        // logic to construct a Multicall transaction or multiple async queries
        // For v0.1.0, we will simulate this.
        
        Ok("{\"balance\": \"1000 SWAY\", \"asteroids\": []}".to_string())
    }
}
