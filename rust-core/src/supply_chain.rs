use std::collections::{HashMap, HashSet};
use anyhow::{Result, Context};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Recipe {
    pub inputs: HashMap<String, u32>,
    pub outputs: HashMap<String, u32>,
    pub process_time_seconds: u32,
}

pub struct SupplyChainGraph {
    recipes: HashMap<String, Recipe>,
    adjacency_list: HashMap<String, Vec<String>>, // Product -> Recipes that produce it
}

impl SupplyChainGraph {
    pub fn new() -> Self {
        SupplyChainGraph {
            recipes: HashMap::new(),
            adjacency_list: HashMap::new(),
        }
    }

    pub fn add_recipe(&mut self, name: &str, recipe: Recipe) {
        self.recipes.insert(name.to_string(), recipe.clone());
        for output in recipe.outputs.keys() {
            self.adjacency_list.entry(output.clone()).or_insert_with(Vec::new).push(name.to_string());
        }
    }

    pub fn find_production_path(&self, target_resource: &str) -> Option<Vec<String>> {
        // Simple BFS/DFS to find a path to produce the target resource
        // This is a simplified version; real implementation would consider costs and inventory.
        if !self.adjacency_list.contains_key(target_resource) {
            return None;
        }
        
        // This is where the recursive "how do I make X?" logic lives.
        // For now, returning the direct recipe names.
        self.adjacency_list.get(target_resource).cloned()
    }
}
