import { relatedSchema } from '@/lib/schema/related'
import { CoreMessage, generateObject } from 'ai'
import {
  getModel,
  getToolCallModel,
  isToolCallSupported
} from '../utils/registry'

export async function generateRelatedQuestions(
  messages: CoreMessage[],
  model: string
) {
  const lastMessages = messages.slice(-1).map(message => ({
    ...message,
    role: 'user'
  })) as CoreMessage[]

  const supportedModel = isToolCallSupported(model)
  const currentModel = supportedModel
    ? getModel(model)
    : getToolCallModel(model)

  const result = await generateObject({
    model: currentModel,
    system: `As a professional finance researcher, your task is to generate a set of three queries that explore financial subject matter more deeply, building upon the initial query and the information uncovered in its search results.

    IMPORTANT: You are a SUPER FINANCE ASSISTANT. You can ONLY generate queries about:
    - Trading (stocks, bonds, commodities, forex, cryptocurrencies)
    - Investment analysis (fundamental analysis, technical analysis, portfolio management)
    - Financial markets and instruments
    - Banking and financial services
    - Fintech innovations and technologies
    - Economic indicators and market trends
    - Financial regulations and compliance
    - Risk management and financial planning

    For instance, if the original query was "Bitcoin price analysis and market trends", your output should follow this format:

    Aim to create queries that progressively delve into more specific aspects, implications, or adjacent topics related to the initial financial query. The goal is to anticipate the user's potential information needs and guide them towards a more comprehensive understanding of the financial subject matter.
    Please match the language of the response to the user's language.`,
    messages: lastMessages,
    schema: relatedSchema
  })

  return result
}
