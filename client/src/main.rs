use std::collections::HashMap;

static SERVER_ADDRESS:&str = "http://127.0.0.1:5000";

async fn register(user_name: &str,
            full_name: (&str, &str),
            gender: &str,
            pronouns: &str,
            interests: (&str, &str, &str, &str, &str),
            loc: (f32, f32),
            age: u32,
            auth: &str) {

    let interests = format!("[{}, {}, {}, {}, {}]", interests.0, interests.1, interests.2, interests.3, interests.4);

    let lat = loc.0.to_string();
    let lng = loc.1.to_string();
    let age = age.to_string();

    let mut map = HashMap::new();
    map.insert("user_name", user_name);
    map.insert("first_name", full_name.0);
    map.insert("last_name", full_name.1);
    map.insert("gender", gender);
    map.insert("pronouns", pronouns);
    map.insert("interests", &interests);
    map.insert("lat", &lat);
    map.insert("lng", &lng);
    map.insert("age", &age);
    map.insert("auth", auth);

    let client = reqwest::Client::new();
    let res = client.post(format!("{}/register", SERVER_ADDRESS))
        .json(&map)
        .send()
        .await
        .unwrap();

    Some(res.status());
}

fn main() {
    let response = register("test", ("test", "test"), "Male", "he/him", ("test", "test", "test", "test", "test"), (69.0, 69.0), 12, "test");
    let response = response.result();
    println!("{}", response);
}
