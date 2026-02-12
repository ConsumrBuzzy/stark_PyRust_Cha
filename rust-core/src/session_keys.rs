use serde::{Deserialize, Serialize};
use anyhow::Result;

// In a real implementation, we would use:
// use starknet::signers::{LocalWallet, SigningKey};
// But for v0.1.0 compilation, we'll keep it simple/mocked.

#[derive(Serialize, Deserialize)]
pub struct SessionKey {
    pub private_key: String,
    pub public_key: String,
    pub expires_at: u64,
}

impl SessionKey {
    /// Generate a new ephemeral session key.
    /// In a real implementation, this would generate a Starknet-compatible key pair.
    /// For this v0.1.0, we simulate the structure.
    pub fn generate() -> Result<Self> {
        // Mock generation for compilation speed/compatibility without full crypto stack setup
        
        let priv_key_hex = "0x1234...ephemeral_private"; 
        let pub_key_hex = "0x5678...ephemeral_public";
        
        Ok(SessionKey {
            private_key: priv_key_hex.to_string(),
            public_key: pub_key_hex.to_string(),
            expires_at: 0, // 0 = indefinite or set later
        })
    }

    /// Create the signed payload that authorizes this session key on the Interact Contract.
    pub fn create_authorization_payload(&self, master_account: &str) -> String {
        format!(
            "{{ \"master\": \"{}\", \"session_pub\": \"{}\", \"action\": \"AUTHORIZE\" }}",
            master_account, self.public_key
        )
    }
}
