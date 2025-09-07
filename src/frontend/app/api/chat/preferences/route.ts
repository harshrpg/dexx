import { getRedisClient } from '@/lib/redis/config'

export async function POST(req: Request) {
    try {
        const { chatId, advancedChatEnabled, advancedChatSymbol } = await req.json()

        if (!chatId || typeof chatId !== 'string') {
            return new Response('chatId is required', { status: 400 })
        }

        const redis = await getRedisClient()
        const pipeline = redis.pipeline()

        // Store as simple fields on chat hash. Upserts if hash does not exist yet.
        pipeline.hmset(`chat:${chatId}`, {
            id: chatId,
            advancedChatEnabled: String(advancedChatEnabled),
            advancedChatSymbol: String(advancedChatSymbol)
        })

        await pipeline.exec()

        return new Response('OK')
    } catch (error) {
        console.error('Failed to persist chat preferences:', error)
        return new Response('Internal Server Error', { status: 500 })
    }
}


